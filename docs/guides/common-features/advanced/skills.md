# Skills Guide (Beta)

Skills are reusable capability modules that can be loaded into cloud sandbox sessions, providing pre-configured tools and scripts for AI agents.

## Overview

The Skills feature provides:

- **Skill Creation**: Create skills locally and push them to the cloud via CLI.
- **Metadata Retrieval**: Query available skills and their descriptions without starting a sandbox.
- **Skill Loading**: Automatically load skills into sandbox sessions at creation time.
- **Skill Filtering**: Filter skills by name for selective loading.

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Skill** | A self-contained capability unit stored as a directory. Must include a `SKILL.md` file, and can optionally contain scripts, configs, or other assets. |
| **SKILL.md** | The metadata file in each skill directory. Uses YAML frontmatter to declare `name` and `description`; the body provides usage instructions for LLMs. |
| **skills_root_path** | The unified root directory for skills in the sandbox (e.g. `/home/wuying/skills`). Determined by the backend based on the sandbox image. Each skill is placed at `{skills_root_path}/{skill_name}/`. |

## Typical Workflow

```
1. Create a skill directory locally with SKILL.md
2. Push it to the cloud via CLI:  agentbay skills push my-skill/
3. Query metadata via SDK:        get_metadata() → list of skills + root path
4. Create a session with skills:  create(load_skills=True) → sandbox has skills loaded
5. Use skills in the sandbox:     read_file("{root}/my-skill/SKILL.md")
```

Steps 3-5 are in SDK code. Step 3 (`get_metadata()`) can run without a sandbox — useful for building LLM prompts before creating sessions. Step 4 tells the backend to actually place skill files into the sandbox.

## Prerequisites

```bash
pip install wuying-agentbay-sdk
export AGENTBAY_API_KEY="your-api-key"
```

## Creating and Publishing Skills (CLI)

Use the `agentbay` CLI to create and manage skills.

### Step 1: Create a Skill Directory

Each skill is a directory containing at least a `SKILL.md` file:

```bash
mkdir my-skill

cat > my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: A useful skill for doing X.
---
# My Skill

Instructions for the AI agent on how to use this skill.

## Usage
1. Read the configuration file at `config.json`
2. Execute the main script with `python main.py`
EOF
```

You can add any additional files the skill needs (scripts, configs, templates, etc.):

```bash
echo '{"key": "value"}' > my-skill/config.json
echo 'print("Hello from my-skill!")' > my-skill/main.py
```

### Step 2: Push to Cloud

```bash
agentbay skills push my-skill/
# Output: Skill "my-skill" created (skill-id: sk-abc123)
```

The `push` command reads `name` and `description` from `SKILL.md`, packages the directory, and uploads it. If a skill with the same name already exists, it will be updated.

### Other CLI Commands

```bash
# List all your skills (your own + public)
agentbay skills list

# View skill details
agentbay skills show <skill-id>

# Delete a skill
agentbay skills delete <skill-id>

# Preview metadata without starting a sandbox
agentbay skills metadata [--name <skill-name>...] [--format json|table]
```

## Querying Skills Metadata (SDK)

Use `get_metadata()` to discover which skills are available and where they will be located in the sandbox — all **without** creating a session. This is especially useful for:

- **Discovering skills** before deciding which to load.
- **Building LLM system prompts** with skill names, descriptions, and file paths before creating a sandbox (supports lazy sandbox startup).

### What `get_metadata()` Returns

| Field | Description |
|-------|-------------|
| `skills_root_path` | The directory path where skills will be installed in the sandbox (e.g. `/home/wuying/skills`). Determined by the backend based on the sandbox image. |
| `skills` | A list of available skill objects, each with `name` and `description` fields (parsed from the `SKILL.md` frontmatter). |

### Example

```python
from agentbay import AgentBay

agent_bay = AgentBay()

# Get all available skills and their root path
meta = agent_bay.beta_skills.get_metadata()
print(f"Root path: {meta.skills_root_path}")  # e.g. "/home/wuying/skills"
print(f"Available skills ({len(meta.skills)}):")
for skill in meta.skills:
    print(f"  - {skill.name}: {skill.description}")
    # Each skill's files will be at: {meta.skills_root_path}/{skill.name}/

# Filter by specific skill names
meta = agent_bay.beta_skills.get_metadata(skill_names=["my-skill"])

# Specify a particular sandbox image
meta = agent_bay.beta_skills.get_metadata(image_id="linux_latest")
```

## Creating Sessions with Skills

Pass `load_skills=True` to `CreateSessionParams` to tell the backend to load skills into the sandbox at creation time. The skill files will appear at the `skills_root_path` returned by `get_metadata()`.

Note: `get_metadata()` only queries metadata; it does **not** load files into the sandbox. You must pass `load_skills=True` when creating a session for skills to actually be present.

```python
from agentbay import AgentBay, CreateSessionParams

agent_bay = AgentBay()

# 1. Query metadata to learn the root path and available skills
meta = agent_bay.beta_skills.get_metadata()
root = meta.skills_root_path  # e.g. "/home/wuying/skills"

# 2. Create a session that loads skills into the sandbox
result = agent_bay.create(CreateSessionParams(load_skills=True))
session = result.session

# 3. Access skill files inside the sandbox
skill_md = session.file_system.read_file(f"{root}/my-skill/SKILL.md")
print(skill_md.content)  # The skill's instructions

# Run a script bundled with the skill
result = session.command.execute_command(f"python3 {root}/my-skill/main.py")
print(result.stdout)

session.delete()
```

## Filtering by Skill Names

To load only a subset of skills, specify `skill_names`:

```python
from agentbay import AgentBay, CreateSessionParams

agent_bay = AgentBay()

params = CreateSessionParams(
    load_skills=True,
    skill_names=["skill-1", "skill-2"],
)
result = agent_bay.create(params)
```

## Multi-Language API Reference

| Language | Service | Method |
|----------|---------|--------|
| Python | `agent_bay.beta_skills` | `get_metadata(image_id?, skill_names?)` |
| TypeScript | `agentBay.betaSkills` | `getMetadata(options?)` |
| Go | `agentBay.BetaSkills` | `GetMetadata(opts?)` |
| Java | `agentBay.getBetaSkills()` | `getMetadata(imageId?, skillNames?)` |

For language-specific examples, see the example files in each SDK's `docs/examples/` directory.
