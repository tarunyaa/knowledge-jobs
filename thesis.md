# Thesis — Knowledge Work Map

Edit this file to update the page text. Sections are delimited by `## <number>. <title>`. The line starting with `CAPTION:` becomes the always-visible caption; everything after it is the body shown when the section is expanded. Tier chips can be embedded in prose as `{T1}`, `{T2}`, `{T3a}`, `{T3b}`, `{T3c}`. Re-render with `uv run python build_site_data.py`.

---

## 1. Introduction

Frontier labs and hardware providers have made the bet through the massive $7 trillion data center build-out that AI will eventually add a lot of value to the economy. The value has to come from the jobs that it can automate, augment, or even create. The issue is that 95% of AI pilot programs within enterprises today deliver little to no measurable impact on profit. This was a finding published by MIT's NANDA initiative in 2025.

Although SOTA LLMs are intelligent, they are unable to deliver gains at the enterprise level. The MIT report points towards flawed enterprise integration. While generic tools like ChatGPT excel for individuals, enterprises operate across a wide suite of data sources, software stacks, and tools. For instance,

The question is *when and how* AI will create real value at the application layer — and three sub-questions sit underneath: when frontier labs become profitable, how AI agents get deployed across enterprises, and how those agents get priced. All three depend on the same thing: how agents are architected into enterprises over the next 12-18 months.

## 2. Defining the nature of knowledge work

Karpathy's Bureau of Labor Statistics visualizer showed that jobs with high digital exposure (~49M of 143M US jobs) are at higher risk of AI restructuring. Zooming in, those jobs are mostly knowledge work. Knowledge work can be defined by labour requiring non-routine problem solving, and as a result, requiring human reasoning abilities.

Every knowledge job requires some mix of three inputs:

- Generic capability: skills that transfer across companies such as writing, coding, analysis, calculation
- Standardized context: information that exists in published or docmentable form within that company
- Tacit context: information that lives in internal workflows, prior decisions, human relationships, unwritten expertise

The ratio of these inputs leads to three categories of knowledge work, and agents that will eventually come for them.

### Tier 1: Genericizable

Jobs within this tier have standard inputs and standard outputs. As a result, the job is similar across employers in terms of skills required and tools used. For example, a software engineer working at Meta and Oracle use the same IDE which is Cursor or VS Code. Another example, a designer at Stripe and Airbnb both use Figma.

Because of highly transferable nature of work within the category, a horizontal agent built once and connected to relevant tools once is good enough. This is built by frontier labs (Claude Code, Codex) or developers building lightweight wrappers. Margins compress the fastest here because every lab can offer roughly the same product.

### Tier 2: Genericizable framework, custom configuration

Jobs within this tier are also similar across companies in the same way as jobs at tier 1. However, an agent built for these jobs require more specific customizations. Connectors alone aren't enough. Take customer service representatives for instance. An agent built for them requires pre-built integrations into Zendesk/Salesforce, a system prompt and escalation logic tuned over thousands of real support conversations, multi-tenant infrastructure, eval dashboards that workers trust, etc.

Examples of agents in this tier are Decagon (customer service), legal research (Harvey), medical scribing (Abridge). As you can see, agents at thie tier are mostly built by vertical agent startups. Recently, there is an effort by frontier labs to use forward deployed engineers or FDEs to target the same verticales.

### Tier 3: Fundamentally custom

These are jobs where tacit context dominates. Work at these jobs cannot be done without knowing things that exist only inside that specific company or the specific human doing the work.

#### Tier 3a: Tacit but fundamental

This is work where the tacit context is currently undocumented but could be extracted through structured interviews, analysis of artifacts, or aggregation of communications. Companies such as Viven and Afterquery are working on this extraction after which the job converts to Tier 2.

#### Tier 3b: Genuinely tacit

This is work where the tacit context cannot be fully articulated even by the worker who has it. The senior engineer's eye that this rocket wing will crumple under pressure, the doctor's diagnosis, the trader's instinct. The only known transfer mechanism is the expert harness-engineering their own agent and iterating with it.

#### Tier 3c: Relational and contextual knowledge

This is work where the tacit context lives in relationships between people rather than in any individual head. Extractable in pieces but loses fidelity because the value is in the relationship. Stays with the company.

*The map below classifies each high-digital-exposure US occupation into one of these tiers. Tile area = total US employment in 2024.*

## 3. Where will the value accrue?

The most consequential battle is being fought at Tier 2. Tier 2 splits along the memory ownership axis.

But the tier framework describes a single architectural layer: per-job-category agents (L1). Enterprises don't deploy one agent at a time. The interesting question is what happens when one company runs Decagon for support, Harvey for legal, Claude Code for engineering, Mercor for recruiting, and a dozen vertical agents besides — all touching overlapping data, overlapping workflows, overlapping definitions of "who is a customer" and "what's a priority account." This is where the cross-agent **orchestration and memory layer** matters (L2). Three architectural choices have emerged:

**Lab-platform memory.** OpenAI Frontier (launched February 2026) and Anthropic Cowork are enterprise platforms that aggregate context across agents into a shared memory store. Crucially, Frontier is **multi-vendor at the agent layer** — it supports OpenAI, Google, Microsoft, Anthropic, and custom-built agents — so the lock-in mechanism, if it operates, isn't the model but the *institutional memory* accumulated in OpenAI-controlled infrastructure. If switching means losing 18 months of business context, model interchangeability doesn't help.

**Incumbent-SaaS memory.** Salesforce Agentforce, ServiceNow Now Assist, Microsoft Copilot Studio: existing systems-of-record building their own agent runtime layer specifically to keep agent execution and context inside their ecosystems. They own the data the agents need; they're defending it.

**Enterprise-owned neutral memory.** Mem0, Sentra, OpenMemory, the broader "company brain" category. The argument (sharply put by the metadata weekly piece on Frontier): enterprises just spent a decade fighting their way out of fragmented business logic across Salesforce / Workday / Snowflake / Databricks — building dbt's semantic layer, MDM platforms, data catalogs — and *"if every platform builds its own business context layer, you don't get a context layer, you get dozens of conflicting context silos."* The neutral case says context must be enterprise-owned and portable, with vendor agents reading from it.

The L1 agent layer is converging toward multi-vendor — even OpenAI accepts this in Frontier's design. **The L2 memory/orchestration layer is the contested ground.**

## 4. State of affairs

A statistic that reframes the field: MIT NANDA's *State of AI in Business 2025* found **95% of enterprise GenAI pilots show no measurable business impact**. The bottleneck isn't model capability; it's deployment. Whoever solves deployment captures the architecture decision — because the engineer doing the deployment chooses where memory lives, which platform agents run on, and what the integration shape is.

**Lab FDE land-grab.** Both labs are buying the deployment channel directly:

- **OpenAI Deployment Company** (May 2026, $4B): joint venture anchored by acquisition of **Tomoro** (~150 forward-deployed engineers, prior deployments at Virgin Atlantic, Fidelity, Supercell, NBA), plus the **Frontier Alliance** routing deployment work through McKinsey, BCG, Accenture, Capgemini.
- **Anthropic's $1.5B joint venture** (May 2026): Blackstone, Hellman & Friedman, Goldman Sachs as founding partners; Apollo, General Atlantic, GIC, Leonard Green, Suko Capital also participating. Targeted at financial services first via Blackstone's portfolio companies.

The $11.5B combined isn't a services business — it's a **control mechanism for the architecture decision** at every customer site. Whoever the FDE works for decides whether the deployment writes memory into Frontier, into Salesforce Agentforce, or into a neutral store like Mem0.

**Vertical agent vendors compete with FDEs at T2.** Decagon, Harvey, Sierra, Abridge, Ambience, Clay sell against the lab-FDE-plus-custom-build alternative. OpenAI's Frontier Partner program brings these verticals inside Frontier so they're not building independently. Whether they're committed to Frontier architecturally or just for distribution is unclear — they're standalone products that could in principle run anywhere.

**Neutral memory ecosystem.** Mem0 ($24M Series A, 41,000 GitHub stars, 186M API calls last quarter, AWS-selected memory provider for the Strands Agents SDK), Sentra ("company brain"), OpenMemory (self-hosted, data sovereignty), Memori (database-agnostic), Animus (model-agnostic core). Viven and Afterquery extract T3a tacit knowledge.

**SaaS incumbents defending data.** Salesforce, Workday, Microsoft, ServiceNow saw stocks punished in early 2026 as Frontier and Cowork were perceived as existential threats. Their response (Agentforce, Now Assist, Copilot Studio) keeps agent execution inside their own ecosystems where the data already lives. **This is a third architecture the thesis previously didn't address: incumbent-SaaS platforms running their own agent layer to defend data lock-in.**

**The neutral architecture's operational gap.** There is no equivalent of the Frontier Alliance on the neutral side — no architecturally-neutral FDE firms at the scale of Tomoro / McKinsey / BCG building deployments designed to be portable across labs. The neutral camp has the philosophy but not the delivery muscle.

## 5. Outcome

**The lab-native case.** Per-seat pricing anchored to salary replacement ($2K/month per AI coworker vs $100K/year per human) produces software margins (70%+) — but only if the enterprise is anchored to a single lab's platform so the "seat" unit stays coherent. The labs are spending $11.5B on the FDE channel because that's the only way the architecture gets designed lab-native by default, which is what per-seat pricing requires.

**The neutral-memory case.** Enterprises just spent a decade building semantic layers, MDM, data catalogs, and lineage tooling specifically to escape the fragmentation Frontier-style platforms re-introduce. Sophisticated buyers will recognize this and demand portability in procurement. Mem0/Sentra-style architectures fit alongside dbt's metrics layer as the agent-era extension of the modern data stack.

**The incumbent-SaaS case.** Salesforce, ServiceNow, Microsoft, Workday own the customer / operational / employee / productivity data the agents need. By building their own L2 layers (Agentforce, Now Assist, Copilot Studio), they hold their share by becoming the agent-platform-of-record for their data domain — neither winning nor losing the broader race, just defending their existing moat.

**The likely equilibrium isn't a single winner.** Per-job agents at T1/T2 will be built by a mix of labs (where FDEs architect the deployment) and vertical startups (where they win speed-to-vertical). The L2 layer fragments three ways: lab-platform memory wins greenfield enterprises that hire lab FDEs; incumbent-SaaS holds existing operational data; neutral memory wins only the buyers sophisticated enough to demand portability AND willing to assemble the rest of the stack themselves.

**The real fulcrum is procurement sophistication, mediated by the FDE channel.** If the metadata-weekly argument — "a decade of data governance pain → demand for portable context" — penetrates enterprise procurement standards over the next 12-18 months, neutral wins disproportionate share. If it doesn't, the labs' $11.5B FDE bet pays off and lab-native takes the new deployments while incumbent SaaS keeps the old data. The neutral side has the right architectural philosophy but lacks the delivery muscle (FDE shops, vertical specialists, deployment patterns) to execute at enterprise scale today. **The 12-18-month race is therefore specifically about whether neutral-FDE delivery emerges fast enough — and whether enterprise procurement creates demand for it before the labs' FDE channel becomes the default.**
