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
    {"summary": f"1 · AI-exposure scoring prompt — filters the map to exposure ≥ "
                f"{MIN_EXPOSURE} (Karpathy's rubric)", "text": EXPOSURE_PROMPT},
    {"summary": "2 · Tier classifier prompt — colours each occupation T1–T3c",
     "text": TIER_PROMPT},
    {"summary": "3 · Tier 2 quadrant prompt — places each T2 job by repeatability × "
                "customer concentration", "text": CELL_PROMPT},
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
        "why": "The workflow packages cleanly and the addressable value sits in a "
               "small cohort of large buyers — a startup builds the operational-context "
               "layer once and sells it across them.",
        "ex": "Decagon · Harvey · Abridge",
    },
    "high-fragmented": {
        "row": "High", "col": "Fragmented", "cls": "c-orange",
        "winner": "Horizontal agents win",
        "why": "Similar everywhere but spread across a long tail of small buyers — the "
               "best general assistant captures the surface. The largest unclaimed pool, "
               "and the labs' real shot.",
        "ex": "Claude · ChatGPT",
    },
    "low-concentrated": {
        "row": "Low", "col": "Concentrated", "cls": "c-purple",
        "winner": "Platform incumbents win",
        "why": "The workflow varies enormously across companies — only the player who "
               "already owns that variation can extend it into AI.",
        "ex": "Salesforce Agentforce · ServiceNow · FIS",
    },
    "low-fragmented": {
        "row": "Low", "col": "Fragmented", "cls": "c-green",
        "winner": "Enterprises go internal",
        "why": "Neither factor is favorable, so capable enterprises build their own "
               "architecture and call lab models as the engine underneath.",
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

    agg = {k: {"jobs": 0, "wages": 0, "occ": 0, "titles": []} for k in QUADRANT_COPY}
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
            "top": [t for _, t in sorted(a["titles"], reverse=True)[:3]],
        }
    return out


def build_map_facts(data):
    """A few data-derived findings for the dropdown beside the map (not the essay)."""
    def pay_weighted(items):
        j = sum((d["jobs"] or 0) for d in items if d.get("pay"))
        w = sum((d["jobs"] or 0) * (d["pay"] or 0) for d in items)
        return (w / j) if j else 0

    t1 = [d for d in data if d.get("tier") == "T1"]
    t2 = [d for d in data if d.get("tier") == "T2"]
    if not t2:
        return []
    pw_t1, pw_t2 = pay_weighted(t1), pay_weighted(t2)
    t2_jobs = sum((d["jobs"] or 0) for d in t2) or 1
    covered = sum((d["jobs"] or 0) for d in t2 if d.get("vendors"))
    admin = sum((d["jobs"] or 0) for d in t2
                if d.get("category") == "office-and-administrative-support")

    return [
        {
            "stat": f"${pw_t2/1000:.0f}K",
            "label": f"Tier 2's pay-weighted average wage — the lowest of any tier "
                     f"(Tier 1 averages ${pw_t1/1000:.0f}K). The biggest T2 segments "
                     f"are admin and clerical, so pricing power is weakest exactly where "
                     f"the employment concentrates.",
        },
        {
            "stat": f"{covered/t2_jobs*100:.0f}%",
            "label": "of Tier 2 employment is in occupations that already have a named "
                     "AI vendor competing today — the operational context is being "
                     "packaged by someone, and rarely by the labs.",
        },
        {
            "stat": f"{admin/1e6:.1f}M",
            "label": f"Tier 2 jobs are office & administrative support "
                     f"({admin/t2_jobs*100:.0f}% of T2) — fragmented long-tail work "
                     f"where no vertical specialist has emerged and a horizontal "
                     f"assistant is the natural winner. No “Decagon for admin” exists yet.",
        },
    ]


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
    map_facts = build_map_facts(data)

    os.makedirs("site", exist_ok=True)
    with open("site/thesis.json", "w", encoding="utf-8") as f:
        json.dump({
            "sections": sections,
            "prompts": PROMPTS,
            "quadrant": quadrant,
            "map_facts": map_facts,
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
