## Official Skills Sandbox (AgentScope)

This cookbook demonstrates how to run **official skills** inside an AgentBay sandbox image and let an AgentScope (Python) agent discover and use them.

### What this cookbook contains

- `main.py`: the runnable entrypoint (end-to-end, no mocks)
- `sandbox_tools.py`: sandbox-backed tool implementations (file system + shell + verification helpers)
- `official_skill_user_scenarios.py`: user-facing prompt scenarios (selected via env var)

### Prerequisites

- **Install dependencies**:
  - `pip install -r cookbook/skills/agentscope-official-skills-sandbox/requirements.txt`
- **Environment variables**:
  - `AGENTBAY_API_KEY`
  - `DASHSCOPE_API_KEY`

### Run

From the repository root:

```bash
python cookbook/skills/agentscope-official-skills-sandbox/main.py
```

### Change the user scenario (prompt)

The user-facing prompts are defined in:

- `cookbook/skills/agentscope-official-skills-sandbox/official_skill_user_scenarios.py`

To switch which scenario is used, set the environment variable `AGENTBAY_OFFICIAL_SKILLS_SCENARIO` (default: `generic`):

```bash
AGENTBAY_OFFICIAL_SKILLS_SCENARIO=seo-audit \
python cookbook/skills/agentscope-official-skills-sandbox/main.py
```

Notes:

- The scenario prompt is written from an end-user perspective and does **not** mention skills or tools.
- The agent is required to write a report into `/tmp` inside the sandbox and open it before finishing.

