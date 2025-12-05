# ubounty Setup Guide

## Installation

### Prerequisites
- Python 3.10 or higher
- Git
- GitHub account with a personal access token
- Anthropic API key (for Claude)

### Install with pip (Development Mode)

```bash
# Clone the repository
git clone https://github.com/1bcMax/ubounty.git
cd ubounty

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

Alternatively, use `uv` for faster installation:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Configuration

### Method 1: Quick Setup (Recommended)

Run the interactive setup:
```bash
ubounty setup
```

This will guide you through:
1. **GitHub Login** - Authenticate via device flow (no need to create tokens manually!)
2. **Anthropic API Key** - Configure your Claude API key

### Method 2: GitHub CLI Login (Easiest)

Simply log in to GitHub:
```bash
ubounty login
```

This will:
1. Show you a code to copy
2. Open GitHub in your browser
3. Authenticate securely without manual token creation
4. Save your credentials locally in `~/.config/ubounty/`

Check your login status:
```bash
ubounty whoami
```

Log out:
```bash
ubounty logout
```

### Method 3: Manual Environment Variables (Alternative)

If you prefer using environment variables:

Copy the example env file:
```bash
cp .env.example .env
```

#### Get your GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "ubounty")
4. Select scopes:
   - `repo` (full control of private repositories)
   - `workflow` (if you want to update GitHub Actions)
5. Click "Generate token" and copy it

Add to `.env`:
```
GITHUB_TOKEN=ghp_your_token_here
```

### Get your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key

Add to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your_key_here
```


## Usage

### Basic Commands

#### Fix an issue
```bash
# Fix issue #42 in the current repository
ubounty fix-issue 42

# Fix issue in a specific repository
ubounty fix-issue 42 --repo owner/repo

# Auto-commit and create PR
ubounty fix-issue 42 --auto-commit --auto-pr
```

#### List issues
```bash
# List open issues in current repo
ubounty list-issues

# List issues in specific repo
ubounty list-issues --repo owner/repo

# Filter by state and labels
ubounty list-issues --state all --labels bug,enhancement
```

#### Check version
```bash
ubounty version
```

### Workflow Example

```bash
# 1. Clone your repository
git clone https://github.com/1bcMax/my-project.git
cd my-project

# 2. List open issues
ubounty list-issues

# 3. Pick an issue and fix it
ubounty fix-issue 15

# 4. Review the suggested fix
# The agent will analyze the issue and suggest code changes

# 5. Apply changes and create PR
ubounty fix-issue 15 --auto-commit --auto-pr
```

## Development

### Run tests
```bash
pytest
```

### Format code
```bash
black ubounty/
ruff check ubounty/
```

### Type checking
```bash
mypy ubounty/
```

## Troubleshooting

### "GitHub token not found"
- Make sure `.env` file exists in the project root
- Verify `GITHUB_TOKEN` is set correctly
- Try running `ubounty setup`

### "Anthropic API key not found"
- Make sure `.env` file exists
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check your API key is valid at https://console.anthropic.com/

### "Repository not found"
- Ensure you're in a git repository
- Verify the repository exists and you have access
- Try specifying `--repo owner/repo` explicitly

## Next Steps

- Check out the [README](README.md) for project overview
- Read about [contributing](CONTRIBUTING.md) (if available)
- Report issues at https://github.com/1bcMax/ubounty/issues
