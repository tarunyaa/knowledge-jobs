"""
Classify each Tier 2 occupation into one of the four cells of the §4 quadrant.

The §4 "Tier 2 battle" argues that packageability of a T2 job is shaped by two
factors, and that each resulting cell has a different likely winner:

                       Concentrated customers     Fragmented customers
    High repeatability   vertical AI startups        horizontal agents
    Low  repeatability   platform incumbents         enterprises go internal

This classifier assigns each of the 51 T2 occupations a (repeatability,
concentration) pair so build_site_data.py can sum real employment and wages
into each cell — turning the qualitative quadrant into a quantified one.

Usage:
    uv run python cell.py
    uv run python cell.py --model claude-opus-4-7
    uv run python cell.py --force
"""

import argparse
import json
import os
import time
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DEFAULT_MODEL = "claude-haiku-4-5"
OUTPUT_FILE = "cells.json"
TIERS_FILE = "tiers.json"

SYSTEM_PROMPT = """\
You are placing a US occupation into a 2x2 grid that predicts who will build \
the dominant AI agent for it. The occupation is already known to be "Tier 2": \
structurally similar across companies, but an agent for it needs company-specific \
operational context (integrations, escalation rules, internal data) to work.

Score the job on two independent axes.

**1. Workflow repeatability across companies** — how similar is the actual \
workflow from one employer to the next?
- **high**: the workflow is nearly the same everywhere; an agent built for one \
company transfers to most others with light configuration. (e.g. customer \
service triage, medical scribing, expense processing, calendar coordination.)
- **low**: the workflow varies enormously across companies because it is wrapped \
around each company's idiosyncratic systems, products, org structure, or \
regulatory posture; an agent must be rebuilt around each company's variation. \
(e.g. sales operations on a bespoke CRM, IT service management, bank-specific \
compliance.)

**2. Company (buyer-market) concentration** — think about the BUYERS of an AI \
agent for this work, NOT how many workers hold the job. Can a single vendor \
capture most of the addressable value by selling one product to a small cohort \
of large organizations?
- **concentrated**: most of the addressable spend/volume sits in a relatively \
small set of large organizations a vendor can serve with shared infrastructure \
— even if the function technically exists at many companies, the value is \
dominated by big buyers. (e.g. customer service at large enterprises with huge \
ticket volume [Decagon's market], big-firm legal review [Harvey], large hospital \
systems [Abridge], money-center bank operations.)
- **fragmented**: the addressable value is spread across a long tail of many \
small and independent buyers with no dominant cohort, so no single vendor can \
serve most of the market with one configuration. (e.g. office administration, \
bookkeeping for small businesses, receptionists, general clerks across every \
small employer.)

Do NOT equate "many people do this job" with fragmented — a high-headcount \
occupation can still have a concentrated buyer market if a few large enterprises \
account for most of the value (customer service is the key example: millions of \
workers, but the agent market is the large-enterprise cohort).

Use the occupation description provided. Return repeatability (high/low), \
concentration (concentrated/fragmented), and a 1-2 sentence rationale.\
"""


class CellClassification(BaseModel):
    repeatability: Literal["high", "low"]
    concentration: Literal["concentrated", "fragmented"]
    rationale: str


def classify(client: anthropic.Anthropic, text: str, model: str) -> CellClassification:
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        output_format=CellClassification,
    )
    return response.parsed_output


def classify_voted(client, text, model, votes):
    """Run the classifier `votes` times; take the majority on each axis independently.

    The two axes are genuinely fuzzy and a few large occupations swing whole cells,
    so a single sample is too noisy. Majority voting stabilises the placement and
    records the tally for transparency.
    """
    rep, con, rationales = [], [], []
    for _ in range(votes):
        r = classify(client, text, model)
        rep.append(r.repeatability)
        con.append(r.concentration)
        rationales.append(r.rationale)
    rep_win = max(set(rep), key=lambda v: (rep.count(v), v == "high"))
    con_win = max(set(con), key=lambda v: (con.count(v), v == "concentrated"))
    # Keep a rationale from a run that agreed with the majority on both axes.
    rationale = next((rationales[i] for i in range(votes)
                      if rep[i] == rep_win and con[i] == con_win), rationales[0])
    return {
        "repeatability": rep_win,
        "concentration": con_win,
        "rationale": rationale,
        "votes": {
            "repeatability": {"high": rep.count("high"), "low": rep.count("low")},
            "concentration": {"concentrated": con.count("concentrated"),
                              "fragmented": con.count("fragmented")},
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--votes", type=int, default=3,
                        help="Samples per occupation; majority wins each axis")
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    with open(TIERS_FILE) as f:
        tiers = json.load(f)
    t2 = [t for t in tiers if t.get("tier") == "T2" and t.get("knowledge_work")]
    print(f"Tier 2 occupations to classify: {len(t2)}")

    cells = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                cells[entry["slug"]] = entry

    print(f"Classifying with {args.model}. Already cached: {len(cells)}")

    errors = []
    client = anthropic.Anthropic()

    for i, occ in enumerate(t2):
        slug = occ["slug"]
        if slug in cells:
            continue

        md_path = f"pages/{slug}.md"
        if not os.path.exists(md_path):
            print(f"  [{i+1}] SKIP {slug} (no markdown)")
            continue

        with open(md_path, encoding="utf-8") as f:
            text = f.read()

        print(f"  [{i+1}/{len(t2)}] {occ['title']}...", end=" ", flush=True)

        try:
            r = classify_voted(client, text, args.model, args.votes)
            cells[slug] = {"slug": slug, "title": occ["title"], **r}
            v = r["votes"]
            print(f"{r['repeatability']} / {r['concentration']} "
                  f"(rep {v['repeatability']['high']}h-{v['repeatability']['low']}l, "
                  f"con {v['concentration']['concentrated']}c-{v['concentration']['fragmented']}f)")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(slug)

        with open(OUTPUT_FILE, "w") as f:
            json.dump(list(cells.values()), f, indent=2)

        if args.delay > 0 and i < len(t2) - 1:
            time.sleep(args.delay)

    print(f"\nDone. Classified {len(cells)} of {len(t2)}, {len(errors)} errors.")
    if errors:
        print(f"Errors: {errors}")

    grid = {}
    for c in cells.values():
        key = f"{c['repeatability']}-{c['concentration']}"
        grid[key] = grid.get(key, 0) + 1
    print("\nCell distribution (occupation count):")
    for key in ("high-concentrated", "high-fragmented", "low-concentrated", "low-fragmented"):
        print(f"  {key:<18} {grid.get(key, 0)}")


if __name__ == "__main__":
    main()
