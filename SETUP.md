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

### Step 1: Log in with GitHub

The CLI uses GitHub OAuth for authentication:

```bash
# Start the login process
ubounty login
```

This will:
1. Display a device code and URL
2. Open your browser to https://github.com/login/device
3. Ask you to enter the code and authorize ubounty
4. Save your GitHub token securely to `~/.config/ubounty/credentials.json`

Verify you're logged in:
```bash
ubounty whoami
```

You should see your GitHub username and wallet status.

### Step 2: Bind Your Wallet (For Bounty Payouts)

To receive bounty payments, you need to bind your Base wallet address:

**Method A: On the Website (Recommended)**
1. Go to https://ubounty.ai/settings
2. Enter your wallet address (0x...)
3. Save

**Method B: Using CLI**
```bash
ubounty wallet bind 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

⚠️ **Important**: Make sure you enter the correct address! Payments cannot be recovered if sent to the wrong address.

Check your wallet status:
```bash
ubounty wallet status
```

### Step 3: Configure Anthropic API (Optional)

If you want to use AI features locally, set up your Anthropic API key:

1. Get your API key from https://console.anthropic.com/
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add:
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

### "Not logged in" or "Authentication required"
- Run `ubounty login` to authenticate with GitHub
- Make sure you complete the device flow authorization in your browser
- Check that `~/.config/ubounty/credentials.json` exists and has correct permissions (should be 0600)

### "Invalid or expired GitHub token"
- Your GitHub token may have expired or been revoked
- Run `ubounty logout` and then `ubounty login` to re-authenticate

### "Anthropic API key not found"
- Make sure `.env` file exists in the project root
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check your API key is valid at https://console.anthropic.com/

### "Repository not found"
- Ensure you're in a git repository
- Verify the repository exists and you have access
- Try specifying `--repo owner/repo` explicitly

### "Invalid wallet address"
- Wallet address must start with `0x` followed by 40 hexadecimal characters
- Example: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
- Double-check you copied the full address

## Next Steps

- Check out the [README](README.md) for project overview
- Read about [contributing](CONTRIBUTING.md) (if available)
- Report issues at https://github.com/1bcMax/ubounty/issues
