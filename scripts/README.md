
# Scripts

This directory contains scripts for code quality checks and repository management.

## Repository Sync

### Handling Squash Merge Conflicts

When using GitHub's "Squash and Merge", the commit history diverges between internal (origin) and external (upstream) repositories. This causes conflicts when syncing back.

**Solution:** After a PR is squash-merged on GitHub, sync from upstream to origin:

```bash
./scripts/sync-from-github.sh
```

This script will:
- Fetch from both remotes
- Reset local main to match upstream/main
- Force push to origin with `--force-with-lease`

**Daily Workflow:**
1. Before starting work: `./scripts/sync-from-github.sh`
2. Develop on feature branches, not main
3. Push feature branch to both remotes
4. Create PR on GitHub, use "Squash and Merge"
5. After PR merges: `./scripts/sync-from-github.sh`

## Code Quality Check

## Usage

### Installing Git Hooks

 After cloning the repository, run the installation script (recommended):：
   ```bash
   chmod +x ./scripts/install-hooks.sh
   ./scripts/install-hooks.sh
   ```

### TypeScript Quality Check

To check TypeScript code quality:

```bash
cd typescript
chmod +x scripts/quality-check.sh
./scripts/quality-check.sh
```

This script will:
1. Run ESLint with auto-fix to fix linting issues
2. Run Prettier to format all TypeScript files
3. Run security scans to check for vulnerabilities
4. Run unit tests to ensure code correctness

Options:
- `--skip-tests`: Skip running tests
- `--skip-security`: Skip security checks
- `--skip-lint`: Skip linting and formatting

### Python Quality Check

To check Python code quality:

```bash
cd python
chmod +x scripts/quality-check.sh
./scripts/quality-check.sh
```

This script will:
1. Run flake8 to check for code issues
2. Run black to format Python files
3. Run bandit to scan for security vulnerabilities
4. Run pip-audit to check for dependency vulnerabilities
5. Run unit tests with coverage reporting

Options:
- `--skip-tests`: Skip running tests
- `--skip-security`: Skip security checks
- `--skip-lint`: Skip linting and formatting

### Golang Quality Check

To check Golang code quality:

```bash
cd golang
chmod +x scripts/quality-check.sh
./scripts/quality-check.sh
```

This script will:
1. Run gofmt and go fmt to format all Go files
2. Run golint to check for style issues
3. Run go vet to analyze code for potential problems
4. Run gosec for security vulnerabilities scanning
5. Run govulncheck for dependency vulnerabilities
6. Run unit tests with coverage

Options:
- `--skip-tests`: Skip running tests
- `--skip-security`: Skip security checks
- `--skip-lint`: Skip linting and formatting
- `--verbose`: Run tests in verbose mode

## CI Integration

These scripts are designed to be run locally before committing changes. They provide the same checks that are run in CI workflows, allowing developers to identify and fix issues before pushing code. It's recommended to run these scripts locally to ensure code meets the project's quality standards.

## Documentation Quality Check

### check_markdown_links.py

A comprehensive tool for checking internal links in markdown documentation.

**Features:**
- ✅ Validates file links and directory links
- ✅ Checks anchor links (heading references)
- ✅ Detects missing README.md files in linked directories
- ✅ Suggests similar anchors for typos
- ✅ Supports both markdown and JSON output formats
- ✅ Can be integrated into CI/CD pipelines

**Basic usage:**

Check all markdown files in the repository:

```bash
python scripts/check_markdown_links.py
```

**CI/CD mode (strict):**

Exit with error code if broken links are found:

```bash
python scripts/check_markdown_links.py --strict
```

**Save report to file:**

```bash
# Markdown format
python scripts/check_markdown_links.py --output link_report.md

# JSON format
python scripts/check_markdown_links.py --output link_report.json --format json
```

**Verbose output:**

```bash
python scripts/check_markdown_links.py --verbose
```

**Exclude additional patterns:**

```bash
python scripts/check_markdown_links.py --exclude "tmp" --exclude "archive"
```

**Check directory README files:**

By default, the tool treats directory links as valid if the directory exists (useful for navigation links). To require README.md files in linked directories:

```bash
python scripts/check_markdown_links.py --check-dir-readme
```

**Example output:**

```
🔍 Scanning markdown files in /path/to/project...
📚 Found 197 markdown files
🔗 Checking internal links...

📊 Results:
  ✅ Valid links: 879
  ❌ Broken links: 3

❌ Found 3 broken link(s):

📄 docs/guide.md
  Line 42: [API Reference](../api/methods.md)
    ⚠️  File not found: api/methods.md
  Line 85: [Configuration](#configuration-options)
    ⚠️  Anchor not found: #configuration-options in docs/guide.md
```

**How it works:**

1. **File Discovery**: Scans all `.md` files recursively, excluding common directories
2. **Heading Extraction**: Parses headings from each markdown file and generates GitHub-style anchors
3. **Link Extraction**: Finds all markdown links using regex pattern matching
4. **Link Validation**:
   - Resolves relative file paths
   - Checks if target files exist
   - Verifies directories have README.md files
   - Validates anchor links against extracted headings
5. **Reporting**: Groups results by source file and provides detailed error messages

**Integration with GitHub Actions:**

```yaml
name: Check Documentation Links

on: [push, pull_request]

jobs:
  check-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Check markdown links
        run: |
          python scripts/check_markdown_links.py --strict --output link_report.md
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: link-check-report
          path: link_report.md
```

## Requirements

- For TypeScript: Node.js and npm with required dependencies
- For Python: Python with flake8, black, bandit, and pip-audit
- For Golang: Go with necessary tools (gofmt, golint, gosec, govulncheck)
- For Documentation Check: Python 3.6+ (no external dependencies)
