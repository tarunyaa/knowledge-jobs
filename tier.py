"""
Classify each high-exposure occupation into a knowledge-work tier using Claude.

Pre-filters to occupations with Karpathy AI Exposure >= 7 (the "high digital
exposure" set), then asks the model to (a) confirm it's knowledge work per the
thesis definition and (b) assign a tier T1 / T2 / T3a / T3b / T3c.

The thesis is that knowledge work splits by how much *tacit context* dominates,
and the deployment shape (lab-native vs neutral memory) follows from the work
mix. This classifier is the per-job evidence for that mix.

Usage:
    uv run python tier.py
    uv run python tier.py --model claude-haiku-4-5
    uv run python tier.py --min-exposure 7
    uv run python tier.py --start 0 --end 10
"""

import argparse
import json
import os
import time
from typing import Literal, Optional

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DEFAULT_MODEL = "claude-opus-4-7"
OUTPUT_FILE = "tiers.json"

SYSTEM_PROMPT = """\
You are classifying US occupations by the **deployment shape of the AI agent \
that would do this job's work**. The axis: how much customization does an AI \
agent need to deploy at an enterprise for this job?

**Tiers:**

- **T1 — Genericizable.** The job has standard inputs and standard outputs \
across companies. The same professional tools are used everywhere (VS Code or \
Cursor for engineers, Figma for designers, Canvas for teachers, Word for \
writers). A horizontal AI agent built once and connected to those standard \
tools is enough to do the work at any company — the "customization" is just \
giving the agent access to the worker's project files. No substantial \
per-customer integration or system-prompt tuning required. Examples: software \
developer (Claude Code works at any company via the codebase), designer, \
translator, copywriter, generic data analyst.

- **T2 — Genericizable framework, custom configuration.** The job is similar \
across companies in skills required, but an AI agent built for it requires \
substantial per-enterprise customization to be useful: pre-built integrations \
into the enterprise's specific tools (Zendesk, Salesforce, internal databases), \
a system prompt and escalation logic tuned over the enterprise's own workflows, \
eval dashboards trusted by the enterprise's workers, multi-tenant infrastructure \
with compliance controls. The same agent *product* serves many enterprises, but \
every enterprise deployment is months of integration and configuration work. \
Examples: customer service representative (Decagon needs Zendesk/Salesforce \
integrations and escalation logic tuned over thousands of conversations), legal \
research (Harvey integrated to a firm's document management), medical scribing \
(Abridge integrated to a hospital's EHR), enterprise sales operations.

- **T3a — Tacit but documentable.** Tacit context dominates the work; a \
horizontal agent can't be built. But the tacit knowledge *could* be extracted \
through structured interviews, artifact analysis, or aggregation of \
communications. Once extracted, the job converts to T2.

- **T3b — Genuinely tacit.** The tacit context cannot be fully articulated even \
by the expert who has it. The senior engineer's eye that this wing will \
crumple, the doctor's clinical gestalt, the trader's instinct. Only the expert \
themselves can build an agent for this work — by harness-engineering it and \
iterating closely.

- **T3c — Relational.** Value lives in established relationships with specific \
people (clients, counterparties, internal stakeholders). An agent can augment \
portable parts of the work (research, drafting, prep) but the relational core \
stays with the human. Examples: senior account executive, partnerships lead, \
high-stakes negotiator.

**Distinguishing T1 vs T2:** The question is *how much customization does the \
agent need to deploy at one enterprise*, not *how transferable are the worker's \
skills*. A customer service rep's skills are highly transferable (generic \
communication) but the agent that automates the role (Decagon) requires deep \
per-enterprise integration — that makes it T2, not T1. A software developer's \
work depends on a specific codebase, but Claude Code accesses that codebase \
through standard tools (git, MCP, the file system) without per-enterprise \
configuration — that makes it T1, not T2.

**Not knowledge work.** If the occupation is primarily physical (electrician, \
nurse), primarily routine clerical (data entry clerk), or primarily performative \
(actor, musician), set knowledge_work=false and leave tier=null.

Return: knowledge_work (bool), tier (T1/T2/T3a/T3b/T3c or null), rationale \
(2-3 sentences explaining what the agent for this job would look like and why \
it fits that tier).\
"""


class TierClassification(BaseModel):
    knowledge_work: bool
    tier: Optional[Literal["T1", "T2", "T3a", "T3b", "T3c"]]
    rationale: str


def classify_occupation(client: anthropic.Anthropic, text: str, model: str) -> TierClassification:
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        output_format=TierClassification,
    )
    return response.parsed_output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--min-exposure", type=int, default=7,
                        help="Pre-filter: only classify occupations with Karpathy "
                             "AI Exposure >= this threshold (default 7)")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Seconds to sleep between requests (SDK already retries on 429)")
    parser.add_argument("--force", action="store_true",
                        help="Re-classify even if already cached")
    args = parser.parse_args()

    with open("occupations.json") as f:
        occupations = json.load(f)
    with open("scores.json") as f:
        scores_by_slug = {s["slug"]: s for s in json.load(f)}

    candidates = [
        o for o in occupations
        if scores_by_slug.get(o["slug"], {}).get("exposure", 0) >= args.min_exposure
    ]
    subset = candidates[args.start:args.end]
    print(f"Filter: AI Exposure >= {args.min_exposure} -> "
          f"{len(candidates)} of {len(occupations)} occupations")

    tiers = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                tiers[entry["slug"]] = entry

    print(f"Classifying {len(subset)} occupations with {args.model}")
    print(f"Already cached: {len(tiers)}")

    errors = []
    client = anthropic.Anthropic()

    for i, occ in enumerate(subset):
        slug = occ["slug"]

        if slug in tiers:
            continue

        md_path = f"pages/{slug}.md"
        if not os.path.exists(md_path):
            print(f"  [{i+1}] SKIP {slug} (no markdown)")
            continue

        with open(md_path, encoding="utf-8") as f:
            text = f.read()

        print(f"  [{i+1}/{len(subset)}] {occ['title']}...", end=" ", flush=True)

        try:
            result = classify_occupation(client, text, args.model)
            tiers[slug] = {
                "slug": slug,
                "title": occ["title"],
                "exposure": scores_by_slug.get(slug, {}).get("exposure"),
                "knowledge_work": result.knowledge_work,
                "tier": result.tier,
                "rationale": result.rationale,
            }
            print(f"knowledge_work={result.knowledge_work} tier={result.tier}")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(slug)

        with open(OUTPUT_FILE, "w") as f:
            json.dump(list(tiers.values()), f, indent=2)

        if args.delay > 0 and i < len(subset) - 1:
            time.sleep(args.delay)

    print(f"\nDone. Classified {len(tiers)} occupations, {len(errors)} errors.")
    if errors:
        print(f"Errors: {errors}")

    vals = [t for t in tiers.values() if t.get("knowledge_work")]
    if vals:
        print(f"\nKnowledge-work occupations: {len(vals)} of {len(tiers)} classified")
        by_tier = {}
        for v in vals:
            t = v.get("tier") or "unknown"
            by_tier[t] = by_tier.get(t, 0) + 1
        print("Distribution (occupation count):")
        for k in sorted(by_tier):
            print(f"  {k}: {'#' * by_tier[k]} ({by_tier[k]})")


if __name__ == "__main__":
    main()
