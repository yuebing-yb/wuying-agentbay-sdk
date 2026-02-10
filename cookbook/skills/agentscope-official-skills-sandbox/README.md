## Official Skills Sandbox (AgentScope)

This cookbook demonstrates how to run **official skills** inside an AgentBay sandbox image and let an AgentScope (Python) agent discover and use them.

### What this cookbook contains

- `python/main.py`: the runnable entrypoint (end-to-end, no mocks)
- `python/sandbox_tools.py`: sandbox-backed tool implementations (file system + shell + verification helpers)
- `python/official_skill_user_scenarios.py`: user-facing prompt scenarios (selected via env var)

### Official skills (name + description)

This list is for quick lookup and may change over time as official skills are updated.

| name | description |
| --- | --- |
| `seo-audit` | When the user wants to audit, review, or diagnose SEO issues on their site. Also use when the user mentions "SEO audit," "technical SEO," "why am I not ranking," "SEO issues," "on-page SEO," "meta tags review," or "SEO health check." For building pages at scale to target keywords, see programmatic-seo. For adding structured data, see schema-markup. |
| `copywriting` | When the user wants to write, rewrite, or improve marketing copy for any page — including homepage, landing pages, pricing pages, feature pages, about pages, or product pages. Also use when the user says "write copy for," "improve this copy," "rewrite this page," "marketing copy," "headline help," or "CTA copy." For email copy, see email-sequence. For popup copy, see popup-cro. |
| `page-cro` | When the user wants to optimize, improve, or increase conversions on any marketing page — including homepage, landing pages, pricing pages, feature pages, or blog posts. Also use when the user says "CRO," "conversion rate optimization," "this page isn't converting," "improve conversions," or "why isn't this page working." For signup/registration flows, see signup-flow-cro. For post-signup activation, see onboarding-cro. For forms outside of signup, see form-cro. For popups/modals, see popup-cro. |
| `pricing-strategy` | When the user wants help with pricing decisions, packaging, or monetization strategy. Also use when the user mentions 'pricing,' 'pricing tiers,' 'freemium,' 'free trial,' 'packaging,' 'price increase,' 'value metric,' 'Van Westendorp,' 'willingness to pay,' or 'monetization.' This skill covers pricing research, tier structure, and packaging strategy. |
| `content-strategy` | When the user wants to plan a content strategy, decide what content to create, or figure out what topics to cover. Also use when the user mentions "content strategy," "what should I write about," "content ideas," "blog strategy," "topic clusters," or "content planning." For writing individual pieces, see copywriting. For SEO-specific audits, see seo-audit. |
| `email-sequence` | When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email program. Also use when the user mentions "email sequence," "drip campaign," "nurture sequence," "onboarding emails," "welcome sequence," "re-engagement emails," "email automation," or "lifecycle emails." For in-app onboarding, see onboarding-cro. |
| `analytics-tracking` | When the user wants to set up, improve, or audit analytics tracking and measurement. Also use when the user mentions "set up tracking," "GA4," "Google Analytics," "conversion tracking," "event tracking," "UTM parameters," "tag manager," "GTM," "analytics implementation," or "tracking plan." For A/B test measurement, see ab-test-setup. |
| `zero-to-launch` | Guides Claude from idea to working prototype using frameworks from OpenAI, Figma, and Airbnb. Use when starting new product features, planning MVP scope, making build-vs-buy decisions, or guiding users from concept to shippable prototype. Applies AI-first thinking (Kevin Weil), simplicity forcing functions (Dylan Field), and complete experience design (Brian Chesky). |
| `ai-product-strategy` | Help users define AI product strategy. Use when someone is building an AI product, deciding where to apply AI in their product, planning an AI roadmap, evaluating build vs buy for AI capabilities, or figuring out how to integrate AI into existing products. |
| `test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code |
| `software-architecture` | Guide for quality focused software architecture. This skill should be used when users want to write code, design architecture, analyze code, in any case that relates to software development. |
| `using-git-worktrees` | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification |

### Prerequisites

- **Environment variables**:
  - `AGENTBAY_API_KEY`
  - `DASHSCOPE_API_KEY`

### Run

From the repository root:

```bash
python cookbook/skills/agentscope-official-skills-sandbox/python/main.py
```

### Change the user scenario (prompt)

The user-facing prompts are defined in:

- `cookbook/skills/agentscope-official-skills-sandbox/python/official_skill_user_scenarios.py`

To switch which scenario is used, set the environment variable `AGENTBAY_OFFICIAL_SKILLS_SCENARIO` (default: `generic`):

```bash
AGENTBAY_OFFICIAL_SKILLS_SCENARIO=seo-audit \
python cookbook/skills/agentscope-official-skills-sandbox/python/main.py
```

Notes:

- The scenario prompt is written from an end-user perspective and does **not** mention skills or tools.
- The agent is required to write a report into `/tmp` inside the sandbox and open it before finishing.

