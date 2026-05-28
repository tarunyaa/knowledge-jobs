# Knowledge Jobs Visualizer — Implementation Plan

## Goal

Fork Karpathy's BLS treemap into a visualization that makes my thesis on AI-agent deployment legible. The thesis argues that knowledge work splits into tiers based on how much tacit context dominates, and that the deployment shape (lab-native vs neutral memory infrastructure) determines where value accrues. The map gives the thesis's quantitative claims (T1 ≈ 20-30%, T2 ≈ 40-50%, T3 ≈ 25-35%) empirical weight against actual BLS employment data.

## How Karpathy's map relates to the thesis

Karpathy's map has one axis: how digital is each job. Color = "AI Exposure" 0-10, where the rubric explicitly says high score means "can be done entirely from a home office on a computer." His conclusion is the breadth claim — look how much of the workforce AI can plausibly touch.

The thesis takes that high-exposure set as **input, not output**. The question isn't *whether* AI touches these jobs (Karpathy answered that) but *what kind of touch* and *who captures the value*. So this visualization:

- **Zooms into the right tail of Karpathy's distribution** (filter to exposure ≥ 7)
- **Recolors by tier** using the thesis framework
- **Lets the reader read off the share-of-employment of each tier** from the treemap directly

Same substrate (employment area, BLS-category grouping); narrower scope; finer question.

## Tier system (per-job classification)

5 categories. **2a vs 2b is NOT encoded per job** — it's a deployment-shape outcome that emerges across the industry, not a property of an occupation. The same legal-research role can be served on Frontier (2a) or on neutral infra (2b); the question is contested at the platform layer, not the job layer.

| Tier  | Definition |
|-------|------------|
| T1    | Genericizable — one agent can work across all companies. Standard inputs, standard outputs, rule/pattern-based. E.g., generic code writing, translation, document summarization, data transformation. |
| T2    | Genericizable framework, custom configuration. Type of work is similar across companies but needs tailoring (RAG over company docs, evals, prompt arch matched to internal workflows). The FDE sweet spot. |
| T3a   | Documentable tacit knowledge. Currently undocumented but extractable via structured interviews, artifact analysis, comms aggregation. Once extracted, converts into T2. |
| T3b   | Genuinely tacit. Cannot be articulated even by the expert. Senior engineer's eye, doctor's diagnosis, trader's instinct. Transfer requires the expert harness-engineering their own agent. |
| T3c   | Relational. Context lives in relationships between people. Extractable in pieces but loses fidelity. Stays with the company. |

## Pipeline

```
existing:  html/ → pages/ → occupations.csv + scores.json
new:                              ↓
                  tier.py (LLM classifier, exposure≥7 only)
                              ↓
                          tiers.json  +  vendors.json (hand-curated)
                              ↓
              build_site_data.py (filter exposure≥7 AND knowledge_work=true)
                              ↓
                          site/data.json
                              ↓
                          site/index.html
```

### Filter

`build_site_data.py` drops occupations with `exposure < 7`. From the existing distribution that leaves **130 occupations / 49M jobs**. The LLM-set `knowledge_work` flag further trims edge cases (e.g., actors are 7/10 in Karpathy's score but don't fit my definition of knowledge work).

### Tier classifier

`tier.py`, modeled on `score.py`:
- Input: occupation Markdown from `pages/<slug>.md`
- Prompt: my knowledge-work definition + 5-tier rubric + examples
- Output JSON: `{ knowledge_work: bool, tier: "T1"|"T2"|"T3a"|"T3b"|"T3c"|null, rationale: str }`
- Incremental checkpointing to `tiers.json`, resumable, same as `score.py`
- Decision: **trust the LLM's share breakdown and update prose to match**, rather than tuning the prompt until shares match my placeholder percentages (more honest — the map can disconfirm the thesis).

### Vendor overlay

`vendors.json` is a small hand-curated map: occupation slug → list of vendor names operating in that segment today. Used in the §4 "State of Affairs" view to make the ecosystem concrete:
- Harvey → lawyers, paralegals, legal assistants
- Decagon → customer service representatives
- Sierra → customer service
- Abridge / Ambience → physicians, surgeons, medical scribes
- Clay → sales reps, account managers

## Frontend

The page is the thesis. The map is the visual payoff embedded inside §2 and re-read by §3 and §4.

Layout:
```
§1 Introduction                                    [collapsible, caption visible]
§2 Mapping the nature of work                      [open by default]
   ── full thesis text on tiers
   ── MAP appears here, default coloring = tiers
   ── legend shows each tier's share of employment
§3 Where will the value accrue?                    [collapsible, caption visible]
   ── opening this section: same map, T2 tiles stay colored, others dim
§4 State of Affairs                                [collapsible]
   ── opening this section: map gets vendor overlay (logos/labels on covered tiles)
§5 Outcome                                         [collapsible]
```

Each section's `<details>` open/close fires `setNarrativeMode(...)` which sets the map render state (which tier is highlighted, vendor overlay on/off). The map itself is a single canvas — same layout, different paint.

### Coloring

Categorical, not gradient. 5 distinct hues for T1/T2/T3a/T3b/T3c. T2 should be visually most prominent since it's the contested middle.

### Tooltip

Title · tier badge · rationale · BLS data (pay/jobs/outlook/education) · Karpathy exposure score for cross-reference. Click → opens BLS page.

## What I'm explicitly *not* doing

- Not assigning 2a/2b per job. That battle is fought above the per-job layer.
- Not keeping the full 342-job dataset. Knowledge work is the scope.
- Not dimming non-knowledge jobs to gray — just filter them out.
- Not replicating Karpathy's 4 toggle layers. The interaction is "scroll through the thesis and watch the same map re-read itself," not "pick a metric."

## Open risks

- LLM tier classification may produce noisy shares. If T2 lands at 30% or 60% rather than 40-50%, the prose updates to match — but I should sanity-check the per-occupation classifications by eye for the largest tiles before publishing.
- The "knowledge work" flag double-filter (exposure ≥ 7 AND LLM says yes) may over-trim. Worth comparing classified counts before vs after the flag.
- Vendor overlay is hand-curated and incomplete by definition; should be presented as "selected examples" not "comprehensive."
