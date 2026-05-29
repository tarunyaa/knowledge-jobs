# Thesis — Knowledge Work Map

Edit this file to update the page text. Sections are delimited by `## <number>. <title>`. The line starting with `CAPTION:` becomes the always-visible caption; everything after it is the body shown when the section is expanded. Tier chips can be embedded in prose as `{T1}`, `{T2}`, `{T3a}`, `{T3b}`, `{T3c}`. Re-render with `uv run python build_site_data.py`.

---

## 1. Introduction

Frontier labs and hardware providers have made the bet through the massive $7 trillion data center build-out that AI will eventually add a lot of value to the economy. The value has to come from the jobs that it can automate, augment, or even create. The issue is that 95% of AI pilot programs within enterprises today deliver little to no measurable impact on profit. This was a finding published by MIT's NANDA initiative in 2025.

Although frontier LLMs are highly capable, most internal enterprise deployments are failing to translate to measurable employee productivity increase. The MIT report points towards flawed enterprise integration. While generic tools like ChatGPT excel for individuals, enterprises operate across a wide suite of data sources, software stacks, and tools. For instance, even preparing for a client meeting requires pulling notes from Notion, the contract from Google Drive, and previous meeting transcripts from Microsoft Teams. A generic LLM won't know to do so.

There is a race being run over the next 12-18 months whose outcome determines how value will be captured at the application layer. The race is not over the model layer — frontier models are converging in capability and are increasingly substitutable. The race is over the layer above the model, where organizational context turns generic capability into useful work. The shape and deployment of AI agents across enterprises will determine where in that layer the durable value lives.

## 2. The Shape of Knowledge Work

Karpathy's Bureau of Labor Statistics visualizer showed that jobs with high digital exposure (~49M of 143M US jobs) are at higher risk of AI restructuring. Zooming in, those jobs are mostly knowledge work. Knowledge work can be defined by labour requiring non-routine problem solving, and as a result, requiring human reasoning abilities.

Every knowledge job requires some mix of three inputs:

- Generic capability: skills that transfer across companies such as writing, coding, analysis, calculation
- Standardized context: information that exists in published or documentable form within that company
- Tacit context: information that lives in internal workflows, prior decisions, human relationships, unwritten expertise

The ratio of these inputs leads to three categories of knowledge work, and agents that will eventually come for them.

### Tier 1: Genericizable

*Horizontal agent is enough*

Jobs within this tier have standard inputs and standard outputs. As a result, the job is similar across employers in terms of skills required and tools used. For example, software engineers at Meta and Oracle use the same IDE — Cursor or VS Code. Another example is a designer at Stripe and Airbnb both using Figma.

Because of highly transferable nature of work within the category, a horizontal agent built once and connected to relevant tools is good enough. This is built by frontier labs (Claude Code, Codex) or developers building lightweight wrappers. Margins compress the fastest here because every lab can offer roughly the same product.

### Tier 2: Genericizable framework, custom configuration

*Vertical agent built first then becomes horizontal*

Jobs within this tier are also similar across companies in the same way as jobs at tier 1. However, an agent built for these jobs requires more specific customizations. Connectors alone aren't enough. Take customer service representatives for instance. An agent built for them requires pre-built integrations into Zendesk/Salesforce, a system prompt and escalation logic tuned over thousands of real support conversations, multi-tenant infrastructure, eval dashboards that workers trust, etc.

Examples of agents in this tier are Decagon (customer service), legal research (Harvey), medical scribing (Abridge). As you can see, agents at this tier are mostly built by vertical agent startups. Recently, there is an effort by frontier labs to use forward deployed engineers or FDEs to target the same verticals.

### Tier 3: Fundamentally custom

*Purely vertical agent*

These are jobs where tacit context dominates. Work at these jobs cannot be done without knowing things that exist only inside that specific company or the specific human doing the work. We've all encountered this in many ways — a senior engineer maintaining a fifteen-year old undocumented tool, an account executive managing a complex enterprise relationship, a manager who is the only one who knows why certain decisions were made. This tier can be further divided.

#### Tier 3a: Documentable tacit knowledge

This is work where the tacit context is currently undocumented but could be extracted through structured interviews or reviewing old email threads and messages. Companies such as Mercor, Viven and Afterquery are working on this extraction after which the job converts to Tier 2.

#### Tier 3b: Genuinely tacit knowledge

This is work where the tacit context cannot be fully articulated even by the worker who has it. The senior engineer's eye that this rocket wing will crumple under pressure, the doctor's diagnosis, the trader's instinct. The only known transfer mechanism is the expert harness engineering their own agent and iterating with it.

#### Tier 3c: Relational and contextual knowledge

This is work where the tacit context lives in relationships between people rather than in any individual head. Extractable in pieces but loses fidelity because the value is in the relationship. No agent can substitute for this.

## 3. The Tier 2 Battle

The most consequential battle is being fought at Tier 2. Both labs have committed roughly $11.5B combined to FDE ventures in 2026.

- **OpenAI's $4B Deployment Company** is backed by TPG, Advent, Bain Capital, and Brookfield, and includes the acquisition of Tomoro, a 150-person applied AI consulting firm. Early OpenAI FDE work deployed agents at Morgan Stanley, BBVA, Klarna, and T-Mobile, which are primarily financial services and customer support names. The acquisition of Tomoro also brought clients in gaming (Supercell), aviation (Virgin Atlantic), retail (Tesco), and consumer goods (Mattel, Red Bull).
- **Anthropic's $1.5B joint venture** is backed by Blackstone, Hellman & Friedman, and Goldman Sachs. Notably, Anthropic has worked with Fidelity National Information Services (FIS) to design the Financial Crimes AI Agent for money laundering investigations. BMO and Amalgamated Bank are the first deployments.

At the same time, startups are creating vertical agents to compete with labs at Tier 2. Decagon, Harvey, Sierra, Abridge, Ambience, and Clay sell against the lab-plus-custom-build alternative for the same enterprise budgets.

The agent landscape is becoming increasingly heterogeneous. A single team might deploy many agents that have to operate as a coherent unit.

Consider a software engineering team running Claude Code for new features, a code review agent for PRs, an on-call agent for production incidents, a deployment agent for release coordination, and Decagon triaging customer-reported bugs into the engineering queue. These agents have to share more than information. They have to share an understanding of how the team actually operates — what counts as good code in this codebase, which incidents the team has learned from, which customer reports are real bugs versus user error, which decisions are settled and which are still contested, which exceptions matter and which can be ignored. Across teams, the question of where that operating model lives becomes the central battle of enterprise AI.

## 4. Where the Lock-In Lives

The history of enterprise shows where the lock-in actually lives. Salesforce did not become entrenched because customer records were difficult to export. ServiceNow did not dominate because tickets were trapped inside its database. Workday did not capture HR because employee data couldn't be moved. In each case, the deeper source of lock-in was that the software became the way the organization performed the function itself. Sales teams operated through Salesforce-defined pipelines. IT departments reorganized around ServiceNow workflows. HR processes became structured around Workday business processes. Although data portability improved over time, organizations stayed because exporting data did not export the workflows, permissions, compliance controls, reporting structures, integrations, and employee habits that had formed around the software.

This strategic asset is what I call the **operational context layer**: the combination of memory, workflow definitions, governance and escalation logic, tool integrations, and the organizational routines that form around them.

An enterprise support agent is valuable not because it remembers previous tickets but because it knows which systems to check, which policies apply, when to escalate, how managers measure performance, and how outcomes are audited. A legal agent is valuable not because it stores prior conversations but because it embeds the firm's review process, risk tolerances, approval chains, and drafting conventions.

## 5. Why Pricing follows Operational Context

Today, labs charge enterprises based on token usage. This works for labs today because they are supply constrained in terms of GPU availability. However, in 2027-2028, when the datacenter buildout completes and compute supply catches up to demand, we will see a Jevons paradox dynamic. When you charge per token, frontier labs compete on price to win the next task to be routed. As inference gets cheaper, customers don't pay less but use more. As a result, the efficiency surplus from declining inference costs gets absorbed into volume rather than captured as margin.

Per-seat pricing breaks this dynamic because it decouples revenue from consumption. Salesforce earned 70%+ gross margins under per-seat pricing because it used deep operational lock-in to capture pricing power. The frontier labs can run the same playbook — charging per AI coworker at salary-replacement rates ($2,000 per month for an agent vs $100,000 per year for the human it replaces) — but only if they're embedded deeply enough in the operational context layer to justify the pricing.

This is why operational context ownership matters. Per-seat pricing only works when the lab owns the entire stack the "seat" runs on — not just the data, but the workflow definitions, the governance, the integration patterns, the organizational routines. The "seat" is a coherent unit only within a single operating system. If the enterprise is composing multiple agents across multiple vendors on a neutral memory layer, the seat dissolves into per-task consumption metrics and pricing reverts to per-token economics.

The Tier 2 battle is therefore about who succeeds in packaging organizational context into repeatable workflows. The winner is whoever becomes the default operating system for a business function.

## 6. The State of Operational Context

Both labs have launched explicit platform plays for owning the operational context layer.

**OpenAI Frontier** (February 2026) is described by OpenAI as "a semantic layer for the enterprise that all AI coworkers can reference to operate and communicate effectively." That phrasing is the operational-context-ownership bet stated directly. Frontier provides agent identities, persistent context, onboarding flows, feedback loops, permissions, and platform-wide governance — all managed on OpenAI's infrastructure. The vertical partner ecosystem (Harvey, Decagon, Sierra, Abridge, Ambience, Clay) plugs into Frontier and inherits its identity and operational model. Named early customers include Intuit, HP, Oracle, State Farm, Uber, and Thermo Fisher.

**Anthropic Claude Cowork** (January 2026) makes the same bet from a different angle. Cowork combines Claude's reasoning model with Microsoft 365 enterprise context, with Claude now available in mainline Microsoft Copilot chat through the Frontier program.

*Note: ChatGPT Enterprise at scale (BBVA's 120,000-employee deployment) is real lab revenue but a different category of product. It's a productivity tool that sits alongside enterprise workflows, not the system the work runs through. The lab-platform operational context bet rises or falls on Frontier and Cowork specifically.*

Anthropic's deal with FIS points in a different direction. The agreement explicitly puts data on FIS infrastructure. But the deeper structure of the deal matters more: FIS is the one doing the operational context restructuring. FIS owns the workflow design for AML investigations, the escalation logic, the governance and audit framework, the regulatory compliance posture, and the relationship with the banks that deploy the agent. Anthropic provides the reasoning engine inside something FIS owns end-to-end. This is the opposite of lab-platform lock-in — and it's the cleanest example of a different pattern: **vertical platform incumbents winning Tier 2 because they already own the operational context for their domain.**

This isn't an exception. The same pattern likely applies in any regulated or operationally complex vertical with established incumbents. Epic and Cerner own the operational context for healthcare. Salesforce owns it for sales operations. ServiceNow owns it for IT workflows. Workday owns it for HR. When labs deploy into these verticals, they're partnering with the incumbent rather than displacing them.

A third pattern is emerging from the **vertical AI startups themselves**. Decagon, Harvey, Sierra, and others aren't just building agents on top of frontier models. They're building the operational context layer for specific functions: the customer support workflow, the legal review process, the medical scribing pipeline. They own the workflow definitions, the evaluation systems, the integrations into customer systems of record, and the accumulated patterns of how the work gets done. The model underneath is increasingly swappable.

A fourth pattern is emerging in parallel: **model-agnostic memory infrastructure** that sits between source systems and agents. The leading vendors are Mem0, OpenMemory, Memori, Animus, and Sentra. Notably, Mem0 raised a $24M Series A in October 2025, and AWS integrated Mem0 as the default memory layer in its Strands Agents SDK.

However, Mem0 abstracts memory but it doesn't build the workflows, governance, and integration patterns that constitute the full operational context layer. The neutral architecture works only when an application company (Decagon, Harvey, a vertical AI startup) builds the operational context on top of neutral memory.

## 7. The Likely Outcome

The Tier 2 layer will not have a single winner. It will fragment based on who succeeds in owning the operational context for each segment:

- **Lab-owned operational context** wins enterprises that prioritize shipping AI fast and accept the lock-in trade-off. Less mature buyers hire lab FDEs to deliver outcomes quickly within their company. The labs capture durable margin here because they own the workflow surface directly.
- **Platform-owned operational context** wins where established enterprise platforms already own the workflow surface. Microsoft Copilot Studio, Salesforce Agentforce, ServiceNow Action Fabric, FIS, and Epic each defend their existing customer relationships by adding AI.
- **Vertical AI startup operational context** wins where new entrants build the operational context layer for a specific function from scratch. Decagon for customer support, Harvey for legal, Sierra for service.

The next 12-18 months will resolve which of these patterns captures the largest share. The labs' $11.5B FDE bet is structured for a world where they win lab-owned operational context at scale. The signals from platform incumbents defending their installed bases and vertical AI startups capturing function-specific workflows suggest that world is contested rather than guaranteed. If lab-owned operational context turns out to be a smaller share of Tier 2 than the bet requires, frontier model margins compress toward inference-reseller economics — not as a prediction of failure, but as a structural feature of competing against players who own the workflow surfaces the agents have to run through.
