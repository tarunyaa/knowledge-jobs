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

MIN_EXPOSURE = 7

# Each section's narrative mode drives how the map repaints itself when the
# section is expanded. See site/index.html.
SECTION_MODE = {
    "1": "default",
    "2": "default",
    "3": "t2-focus",
    "4": "vendors",
    "5": "default",
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
        return

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


def tier_chip_html(match: re.Match) -> str:
    tier = match.group(1)
    cls = tier.lower()
    return f'<span class="tier-chip {cls}">{tier}</span>'


def render_markdown(text: str) -> str:
    html = markdown.markdown(text, extensions=["extra"])
    return TIER_CHIP_RE.sub(tier_chip_html, html)


def build_thesis():
    if not os.path.exists("thesis.md"):
        print("(skipping thesis.json — thesis.md not found)")
        return

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

    os.makedirs("site", exist_ok=True)
    with open("site/thesis.json", "w", encoding="utf-8") as f:
        json.dump({
            "sections": sections,
            "scoring_prompt": TIER_PROMPT,
        }, f)

    print()
    print(f"Wrote {len(sections)} thesis sections to site/thesis.json")
    for s in sections:
        print(f"  §{s['id']} {s['title']:<40} mode={s['mode']}")


def main():
    build_occupations()
    build_thesis()


if __name__ == "__main__":
    main()
