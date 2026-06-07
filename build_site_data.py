"""
Build site/data.json (occupations) and site/thesis.json (prose) for the frontend.

- Reads occupations.csv (stats), scores.json (Karpathy AI exposure), tiers.json
  (per-job tier classification), and vendors.json (vendor overlay for §4).
- Filters to occupations passing both gates: Karpathy exposure >= MIN_EXPOSURE
  AND the LLM classifier marked knowledge_work=true. Writes site/data.json.
- Reads thesis.md, splits sections, renders markdown to HTML, substitutes tier
  chips, writes site/thesis.json.

Usage:
    uv run python build_site_data.py
"""

import csv
import json
import os
import re

import markdown

from tier import SYSTEM_PROMPT as TIER_PROMPT
from score import SYSTEM_PROMPT as EXPOSURE_PROMPT
from cell import SYSTEM_PROMPT as CELL_PROMPT

MIN_EXPOSURE = 7

# The LLM prompts behind the visualization, surfaced as dropdowns (à la Karpathy).
PROMPTS = [
    {"summary": f"1 · AI-exposure scoring prompt: filters the map to exposure ≥ "
                f"{MIN_EXPOSURE} (Karpathy's rubric)", "text": EXPOSURE_PROMPT},
    {"summary": "2 · Tier classifier prompt: colours each occupation T1 to T3c",
     "text": TIER_PROMPT},
    {"summary": "3 · Tier 2 quadrant prompt: places each T2 job by repeatability and "
                "company concentration", "text": CELL_PROMPT},
]

# Each section's narrative mode drives how the map repaints itself when the
# section is expanded. See site/index.html.
SECTION_MODE = {
    "1": "default",     # The puzzle
    "2": "default",     # The FDE bet, reframed
    "3": "default",     # The Shape of Knowledge Work — tier coloring (map sits after this)
    "4": "t2-focus",    # The Tier 2 battle — highlight T2
    "5": "default",     # Supply-side economics
    "6": "vendors",     # Unit economics — show who owns each surface
}

TIER_CHIP_RE = re.compile(r"\{(T1|T2|T3a|T3b|T3c)\}")


def build_occupations():
    with open("scores.json") as f:
        scores = {s["slug"]: s for s in json.load(f)}

    tiers = {}
    if os.path.exists("tiers.json"):
        with open("tiers.json") as f:
            tiers = {t["slug"]: t for t in json.load(f)}

    vendors = {}
    if os.path.exists("vendors.json"):
        with open("vendors.json") as f:
            raw = json.load(f)
            vendors = {k: v for k, v in raw.items() if not k.startswith("_")}

    with open("occupations.csv") as f:
        rows = list(csv.DictReader(f))

    data = []
    dropped_low_exposure = 0
    dropped_not_knowledge = 0
    dropped_no_classification = 0

    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        tier = tiers.get(slug, {})
        exposure = score.get("exposure")

        if exposure is None or exposure < MIN_EXPOSURE:
            dropped_low_exposure += 1
            continue

        if not tier:
            dropped_no_classification += 1
            continue

        if not tier.get("knowledge_work"):
            dropped_not_knowledge += 1
            continue

        data.append({
            "title": row["title"],
            "slug": slug,
            "category": row["category"],
            "pay": int(row["median_pay_annual"]) if row["median_pay_annual"] else None,
            "jobs": int(row["num_jobs_2024"]) if row["num_jobs_2024"] else None,
            "outlook": int(row["outlook_pct"]) if row["outlook_pct"] else None,
            "outlook_desc": row["outlook_desc"],
            "education": row["entry_education"],
            "exposure": exposure,
            "exposure_rationale": score.get("rationale"),
            "tier": tier.get("tier"),
            "tier_rationale": tier.get("rationale"),
            "vendors": vendors.get(slug, []),
            "url": row.get("url", ""),
        })

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as f:
        json.dump(data, f)

    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Wrote {len(data)} occupations to site/data.json")
    print(f"Total jobs represented: {total_jobs:,}")
    print()
    print(f"Filter funnel (from {len(rows)} BLS occupations):")
    print(f"  dropped exposure < {MIN_EXPOSURE}:   {dropped_low_exposure}")
    print(f"  dropped no tier classification:       {dropped_no_classification}")
    print(f"  dropped knowledge_work=false:         {dropped_not_knowledge}")
    print(f"  kept:                                 {len(data)}")

    if not data:
        return data

    print()
    by_tier = {}
    for d in data:
        t = d["tier"] or "unknown"
        by_tier.setdefault(t, {"count": 0, "jobs": 0})
        by_tier[t]["count"] += 1
        by_tier[t]["jobs"] += d.get("jobs") or 0
    print("Tier shares (kept set):")
    for t in sorted(by_tier):
        c = by_tier[t]["count"]
        j = by_tier[t]["jobs"]
        pct = j / total_jobs * 100 if total_jobs else 0
        print(f"  {t:<5} {c:>3} occ   {j:>12,} jobs   {pct:>5.1f}% of employment")

    return data


def tier_chip_html(match: re.Match) -> str:
    tier = match.group(1)
    cls = tier.lower()
    return f'<span class="tier-chip {cls}">{tier}</span>'


def render_markdown(text: str) -> str:
    html = markdown.markdown(text, extensions=["extra"])
    return TIER_CHIP_RE.sub(tier_chip_html, html)


# Editorial copy for each quadrant cell; employment/wage stats are merged in
# from cells.json + the kept occupation set at build time.
QUADRANT_COPY = {
    "high-concentrated": {
        "row": "High", "col": "Concentrated", "cls": "c-blue",
        "winner": "Vertical AI startups win",
        "why": "When the job packages cleanly and a small cohort of large companies can "
               "use the same infrastructure, a startup can build the operational context "
               "layer once and sell it to them.",
        "ex": "Decagon · Harvey · Abridge",
    },
    "high-fragmented": {
        "row": "High", "col": "Fragmented", "cls": "c-orange",
        "winner": "Horizontal agents win",
        "why": "When jobs are similar everywhere but not exactly, a horizontal agent "
               "captures the surface. Most admin and secretary work falls here. The "
               "largest unclaimed cell, and the one the labs have a real shot at.",
        "ex": "Claude managed agents · OpenAI workspace agents · Microsoft Copilot",
    },
    "low-concentrated": {
        "row": "Low", "col": "Concentrated", "cls": "c-purple",
        "winner": "Platform incumbents win",
        "why": "When jobs vary significantly across companies, only players who already "
               "own that variation can extend it into AI. The incumbent's existing "
               "operational context does the work.",
        "ex": "Salesforce Agentforce · ServiceNow · FIS",
    },
    "low-fragmented": {
        "row": "Low", "col": "Fragmented", "cls": "c-green",
        "winner": "Enterprises go internal",
        "why": "When neither factor is favorable, technically capable enterprises build "
               "their own architectures. Lab models serve as reasoning engines called "
               "into context infrastructure the enterprise owns.",
        "ex": "JPMorgan LLM Suite · Bridgewater",
    },
}


def build_quadrant(data):
    """Sum T2 employment/wages into the four §4 cells using cells.json.

    Placement comes from the buyer-market classifier (cells.json); the number on
    each cell is the *prize* (employment and wages), not the axis.
    """
    if not os.path.exists("cells.json"):
        print("(no cells.json — run `uv run python cell.py`; quadrant left unquantified)")
        return None
    with open("cells.json") as f:
        cells = {c["slug"]: c for c in json.load(f)}

    agg = {k: {"jobs": 0, "wages": 0, "occ": 0, "titles": [], "ow_num": 0, "ow_den": 0}
           for k in QUADRANT_COPY}
    for d in data:
        if d.get("tier") != "T2":
            continue
        c = cells.get(d["slug"])
        if not c:
            continue
        key = f"{c['repeatability']}-{c['concentration']}"
        if key not in agg:
            continue
        jobs = d.get("jobs") or 0
        agg[key]["jobs"] += jobs
        agg[key]["wages"] += jobs * (d.get("pay") or 0)
        agg[key]["occ"] += 1
        agg[key]["titles"].append((jobs, d["title"]))
        if d.get("outlook") is not None:
            agg[key]["ow_num"] += jobs * d["outlook"]
            agg[key]["ow_den"] += jobs

    total_jobs = sum(a["jobs"] for a in agg.values()) or 1
    out = {}
    for key, copy in QUADRANT_COPY.items():
        a = agg[key]
        out[key] = {
            **copy,
            "jobs": a["jobs"],
            "wages": a["wages"],
            "occ": a["occ"],
            "pct": round(a["jobs"] / total_jobs * 100, 1),
            "pay": round(a["wages"] / a["jobs"]) if a["jobs"] else 0,
            "outlook": round(a["ow_num"] / a["ow_den"], 1) if a["ow_den"] else 0,
            "top": [t for _, t in sorted(a["titles"], reverse=True)[:3]],
        }
    return out


def _pay_weighted(items):
    j = sum((d["jobs"] or 0) for d in items if d.get("pay"))
    w = sum((d["jobs"] or 0) * (d["pay"] or 0) for d in items)
    return (w / j) if j else 0


def build_map_facts(data, quadrant):
    """Three coherent, high-impact findings for the dropdown beside the map."""
    total_jobs = sum((d["jobs"] or 0) for d in data) or 1
    facts = []

    if quadrant:
        labs = quadrant["high-fragmented"]
        inc = quadrant["low-concentrated"]
        facts.append({
            "stat": f"{labs['outlook']:+.0f}%",
            "label": f"The one cell the labs can win is the largest in Tier 2 "
                     f"(${labs['wages']/1e9:.0f}B in wages) but the lowest-paid, at "
                     f"${labs['pay']/1000:.0f}K, and BLS projects its employment to "
                     f"shrink {abs(labs['outlook']):.0f}% this decade. The labs win on "
                     f"volume, not value.",
        })
        facts.append({
            "stat": f"{inc['outlook']:+.0f}%",
            "label": f"The high-value work, ${inc['pay']/1000:.0f}K jobs that hold a third "
                     f"of all Tier 2 wages, sits in the low-repeatability cell platform "
                     f"incumbents already own (Salesforce, ServiceNow, FIS). It is growing "
                     f"while the labs' cell declines. Incumbents keep the margin and the "
                     f"growth.",
        })

    t3c = [d for d in data if d.get("tier") == "T3c"]
    if t3c:
        w = sum((d["jobs"] or 0) * (d["pay"] or 0) for d in t3c)
        j = sum((d["jobs"] or 0) for d in t3c)
        facts.append({
            "stat": f"${w/1e12:.1f}T",
            "label": f"Relational work (Tier 3c) is the second-largest wage pool in "
                     f"knowledge work, {j/1e6:.1f}M jobs worth ${w/1e12:.1f}T a year. It "
                     f"lives in relationships between people and is structurally out of "
                     f"reach for any agent.",
        })
    return facts


TIER_LABEL = {
    "T1": "Genericizable", "T2": "Framework + config", "T3a": "Documentable tacit",
    "T3b": "Genuinely tacit", "T3c": "Relational",
}
TIER_INSIGHT = {
    "T1": "The labs' direct territory through Claude Code and Codex: the highest AI "
          "exposure and the fastest projected growth, but small headcount and heavy "
          "token burn per task.",
    "T2": "The battleground. Huge by headcount yet the lowest-paid tier, with "
          "essentially flat projected growth, the prize is wide, cheap, and barely "
          "expanding.",
    "T3a": "Tacit but documentable. Once firms like Mercor and Viven extract the "
           "context, these jobs convert into Tier 2.",
    "T3b": "The highest-paid tier. The context is genuinely tacit, so only the expert "
           "can harness-engineer the agent.",
    "T3c": "The second-largest wage pool in knowledge work after Tier 2. It lives in "
           "relationships between people and is structurally out of reach for any agent.",
}


def build_tier_stats(data):
    """Per-tier stat cards for the 'each tier at a glance' dropdown (à la Karpathy)."""
    total_jobs = sum((d["jobs"] or 0) for d in data) or 1

    def emp_weighted(items, key):
        j = sum((d["jobs"] or 0) for d in items if d.get(key) is not None)
        s = sum((d["jobs"] or 0) * d[key] for d in items if d.get(key) is not None)
        return (s / j) if j else 0

    out = []
    for t in ["T1", "T2", "T3a", "T3b", "T3c"]:
        it = [d for d in data if d.get("tier") == t]
        if not it:
            continue
        jobs = sum((d["jobs"] or 0) for d in it)
        top = sorted(it, key=lambda d: -(d["jobs"] or 0))[:3]
        out.append({
            "tier": t,
            "label": TIER_LABEL[t],
            "jobs": jobs,
            "pct": round(jobs / total_jobs * 100, 1),
            "pay": round(_pay_weighted(it)),
            "outlook": round(emp_weighted(it, "outlook"), 1),
            "exposure": round(emp_weighted(it, "exposure"), 1),
            "top": [d["title"] for d in top],
            "insight": TIER_INSIGHT[t],
        })
    return out


def build_thesis(data):
    if not os.path.exists("thesis.md"):
        print("(skipping thesis.json — thesis.md not found)")
        return
    data = data or []

    with open("thesis.md", encoding="utf-8") as f:
        raw = f.read()

    section_blocks = re.split(r"\n## (\d+)\.\s+", "\n" + raw)
    sections = []
    for i in range(1, len(section_blocks), 2):
        num = section_blocks[i]
        block = section_blocks[i + 1].strip()
        first_newline = block.find("\n")
        if first_newline == -1:
            continue
        title = block[:first_newline].strip()
        rest = block[first_newline + 1:].strip()

        caption = ""
        body_md = rest
        caption_match = re.match(r"CAPTION:\s*(.*?)(?:\n\s*\n|\Z)", rest, re.DOTALL)
        if caption_match:
            caption = caption_match.group(1).strip()
            body_md = rest[caption_match.end():].strip()

        sections.append({
            "id": num,
            "title": title,
            "caption_html": render_markdown(caption) if caption else "",
            "body_html": render_markdown(body_md) if body_md else "",
            "mode": SECTION_MODE.get(num, "default"),
        })

    quadrant = build_quadrant(data)
    map_facts = build_map_facts(data, quadrant)
    tier_stats = build_tier_stats(data)

    os.makedirs("site", exist_ok=True)
    with open("site/thesis.json", "w", encoding="utf-8") as f:
        json.dump({
            "sections": sections,
            "prompts": PROMPTS,
            "quadrant": quadrant,
            "map_facts": map_facts,
            "tier_stats": tier_stats,
        }, f)

    print()
    print(f"Wrote {len(sections)} thesis sections to site/thesis.json")
    for s in sections:
        print(f"  §{s['id']} {s['title']:<40} mode={s['mode']}")

    if quadrant:
        print("\nQuadrant cells (T2 prize by employment):")
        for key, c in quadrant.items():
            print(f"  {key:<18} {c['occ']:>2} occ  {c['jobs']:>12,} jobs  "
                  f"{c['pct']:>5.1f}%  ${c['wages']/1e9:>5.0f}B  -> {c['winner']}")


def main():
    data = build_occupations()
    build_thesis(data)


if __name__ == "__main__":
    main()
