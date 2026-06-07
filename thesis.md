# Thesis: Knowledge Work Map

Edit this file to update the page text. Sections are delimited by `## <number>. <title>`. The line starting with `CAPTION:` becomes the always-visible caption; the body follows. Tier chips can be embedded in prose as `{T1}`, `{T2}`, `{T3a}`, `{T3b}`, `{T3c}`. The `{{TIER2_MATRIX}}` token is replaced by the 2x2 quadrant diagram. Re-render with `uv run python build_site_data.py`.

---

## 1. The puzzle

CAPTION: Two moves the labs made in 2026 seem to point in opposite directions.

Anthropic is rumored to be about to have its [first profitable quarter](https://techcrunch.com/2026/05/20/anthropic-says-its-about-to-have-its-first-profitable-quarter/) and both frontier labs are targeting IPO. I've been trying to piece together what their long-term business model is going to be.

**Puzzle piece 1:** On May 4 2026, both labs revealed enterprise AI joint ventures with private equity and finance partners.

- [Anthropic's $1.5B partnership with Blackstone, Hellman & Friedman, and Goldman Sachs](https://www.anthropic.com/news/enterprise-ai-services-company)
- [OpenAI's $4B Deployment Company backed by TPG, Advent, Bain Capital, and Brookfield](https://openai.com/index/openai-launches-the-deployment-company/)

Both ventures use the same structural play from Palantir's book: embedding forward deployed engineers inside enterprise customers to redesign workflows around AI models.

**Puzzle piece 2:** A few months earlier, as [Simon Willison](https://simonwillison.net/2026/May/27/product-market-fit/#enterprise-customers-are-now-paying-api-prices) explained, both labs converted their enterprise customers from subscription bundles to consumption-based billing. Heavy users of Claude Code and Codex now cost enterprises $1,000+ per month per seat, 30x what flat-rate subscriptions cost the year before. Uber maxed out its annual AI budget within months of 2026.

The puzzle is that these moves seemingly point in different directions.

The joint ventures bet on owning workflow surfaces inside enterprise customers: becoming the system of record, achieving lock-in, and commanding margins similar to the per-seat economics of the SaaS era.

The pricing pivots bet on capturing revenue proportional to how many tokens enterprise customers consume, the per-token economics of API calls.

But the more I looked, the more I think they're the same bet.

## 2. The FDE bet, reframed

CAPTION: The joint ventures look like system of record plays but operational context doesn't reach the labs.

The standard read of the joint ventures is that they're system of record plays.

The history of enterprise software shows what it means to become the system of record. When Salesforce first arrived, it was a tool sitting alongside how the sales team already did its work. Over time, the relationship inverted. The pipeline stages became Salesforce-defined stages. The lead qualification process became the qualification rules baked into Salesforce. The sales team's pipeline became Salesforce and the same pattern played out with ServiceNow in IT and Workday in HR.

The same pattern could in principle work for AI agents. A customer service agent could accumulate the company's specific escalation patterns, plug into its systems, and own the operational context of how the workflow actually runs, eventually becoming the surface where customer service work actually executes.

The problem however is that the operational context doesn't transfer to the labs. The deployments confirm this. Anthropic's deal with FIS for the Financial Crimes AI agent states that operational context, what counts as suspicious activity at BMO versus Amalgamated, which alerts get escalated, how investigators document findings, stays with FIS. OpenAI Frontier is structured the same way, launching with vertical AI startups as Frontier Partners rather than competitors. The labs provide the models underneath. The operational context lives somewhere else.

To see why, we need to look at the shape of the work AI is actually being deployed against.

## 3. The shape of knowledge work

CAPTION: Generic capability, standardized context, tacit context. The mix decides which agent can do the job, and classifies jobs across tiers.

[Karpathy's Bureau of Labor Statistics visualizer](https://karpathy.ai/jobs/) showed that jobs with high digital exposure, roughly 49 million of 143 million US jobs, are at higher risk of AI restructuring. Those jobs are mostly knowledge work: labor requiring non-routine problem solving and human reasoning.

Every knowledge job requires some mix of three inputs:

- Generic capability: skills that transfer across companies such as writing, coding, analysis, calculation
- Standardized context: information that exists in a documentable form within that company
- Tacit context: information that lives in workflows, prior decisions, relationships

The ratio of these inputs determines which agent works for which job. Three tiers emerge.

### {T1} Tier 1: Genericizable

*Horizontal agent is enough*

Jobs in this tier have standard inputs and standard outputs and are similar across employers. Software engineers at Meta and Oracle use the same IDE, Cursor or VS Code. Designers at Stripe and Airbnb both use Figma. Because the work is highly transferable, a horizontal agent built once and connected to relevant tools is good enough. This is built by frontier labs (Claude Code, Codex) or developers building lightweight wrappers. Margins compress fastest here because every lab can offer roughly the same product, but token consumption per task is high.

### {T2} Tier 2: Genericizable framework, custom configuration

*Vertical or horizontal agent*

Tier 2 jobs are structurally similar across companies but require company-specific context to execute. Customer service has the same shape at Goldman and JPMorgan, but an agent needs each company's actual escalation rules, support history, and customer data to do the work. Connectors alone aren't enough. Examples of agents in this tier are Decagon (customer service), Harvey (legal research), and Abridge (medical scribing). Agents at this tier are mostly built by vertical agent startups. Recently, frontier labs have started using FDEs to target the same verticals.

### Tier 3: Fundamentally custom

*Purely vertical agent*

These are jobs where tacit context dominates. Work at these jobs cannot be done without knowing things that exist only inside that specific company or the specific human doing the work. We've all encountered this in many ways: a senior engineer maintaining a fifteen-year-old undocumented tool, an account executive managing a complex enterprise relationship, a manager who is the only one who knows why certain decisions were made. This tier can be further divided.

<details class="subtier-toggle">
<summary>Drop down to see the three kinds of Tier 3 work</summary>
<p>{T3a} <strong>Tier 3a: Documentable tacit knowledge.</strong> This is work where the tacit context is currently undocumented but could be extracted through structured interviews or reviewing old email threads and messages. Companies such as Mercor, Viven and Afterquery are working on this extraction after which the job converts to Tier 2.</p>
<p>{T3b} <strong>Tier 3b: Genuinely tacit knowledge.</strong> This is work where the tacit context cannot be fully articulated even by the worker who has it. The senior engineer's eye that this rocket wing will crumple under pressure, the doctor's diagnosis, the trader's instinct. The only known transfer mechanism is the expert harness engineering their own agent and iterating with it.</p>
<p>{T3c} <strong>Tier 3c: Relational and contextual knowledge.</strong> This is work where the tacit context lives in relationships between people rather than in any individual head. Extractable in pieces but loses fidelity because the value is in the relationship. No agent can come for this. On the map it is the largest tier outside the Tier 2 battle, 26% of high-exposure knowledge work and 11.6 million jobs.</p>
</details>

## 4. The Tier 2 battle

CAPTION: 60% of knowledge work, four cells, four different probable winners.

The most consequential battle is being fought at {T2} which is 60% of knowledge work: **27 million jobs and $1.75 trillion in annual wages.**

Tier 2 work needs the operational context of that company to be packaged in forms that agents can ingest. MCPs, tools, database connections, prompt scaffolds. But packageability isn't uniform across Tier 2. Two factors shape it.

- **Workflow repeatability across companies.** Does customer service look the same at Goldman as at JPMorgan?
- **Company concentration.** Is the work concentrated in a few large companies, or spread across many small ones?

These produce four cells, and each has a likely winner.

{{TIER2_MATRIX}}

The labs are spending $5.5B through FDE ventures, but the deployments target the concentrated, high-value verticals: finance, healthcare, and manufacturing at large enterprises. That is the left side of the map, where operational context stays with the incumbent or the enterprise, as the FIS deal showed. The one cell the labs can win on their own is horizontal agents for fragmented work. It is the largest cell in Tier 2 by employment, 16 million jobs and $848B in wages, but it is the lowest paid at around $52K. The high-value work, the $108K jobs that make up a third of all Tier 2 wages, sits in the low repeatability and concentrated cell that platform incumbents like Salesforce and ServiceNow already own.

But a horizontal agent is generic by definition. Even in the cell they win, there is no operational context to lock in. There aren't many structural incentives for operational context to transfer into frontier labs.

So if the FDE play isn't to become the system of record, what is it for?

My hypothesis: it's a way to generate demand.

## 5. Supply side economics

CAPTION: A $7T datacenter buildout only pays off if enterprises burn the tokens. That is what the FDEs are for.

Today, frontier labs can command premium prices for tokens because compute remains scarce. This is why we saw their pricing pivot with puzzle piece 2.

At the same time, the labs have invested unprecedented sums into expanding supply. The [$7T datacenter buildout](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-7-trillion-dollar-data-center-build-out-how-industrials-can-capture-their-share#/) is going to complete in 2027-2028, dramatically increasing the number of GPUs available.

Unless frontier labs can utilize all the new GPU supply, inference commoditizes and their margins collapse. And enterprises are the only market large enough to absorb that volume of GPUs.

The hiccup is that enterprises struggle to integrate AI into their existing workflows. Enterprises rarely have clean data, tools connected to MCP servers or documented context. FDEs solve this problem by doing the messy work of adoption and redesigning workflows around AI. Their job is to convert AI capability into better gross margins for the enterprise.

Viewed through that lens, the labs aren't trying to capture the workflows. They're trying to make sure the workflows get built. And that every one of them continuously burns lab tokens.

## 6. What this means for unit economics

CAPTION: AWS's playbook, not Salesforce's: sit underneath everything and get paid by the token.

The frontier labs are running AWS's playbook, not Salesforce's.

AWS never needed to own the applications built on top of it. It only needed those applications to exist. Every successful startup, internal tool, and SaaS company increased demand for AWS infrastructure.

The same logic applies here. Most operational context is likely to remain outside the labs. The labs provide the reasoning layer underneath and capture value through metered inference. This produces real businesses with Anthropic approaching its first profitable quarter at $10.9B revenue, but at infrastructure economics rather than SaaS economics.

Seen this way, the $5.5 billion being spent on FDE-led deployments is not a system of record investment. It is a demand generation investment. And it's also the labs' admission that demand might not scale fast enough on its own. The next 18 months reveal whether $5.5B of demand generation can force the curve.
