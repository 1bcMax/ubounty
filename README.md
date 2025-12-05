# ubounty

Enable maintainers to clear their backlog with one command. Turn "I'll fix this someday" into "Done in 5 minutes."

## Quick Start

```bash
# 1. Install CLI
pip install -e .

# 2. Log in with GitHub
ubounty login

# 3. Check your wallet status
ubounty whoami

# 4. (Optional) Bind your wallet for bounty payouts
ubounty wallet bind 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

# 5. Start fixing issues (coming soon!)
ubounty fix-issue 42
```

## Features

- **Easy GitHub Authentication** - Log in with `ubounty login` using GitHub device flow
- **Wallet Integration** - View and manage your Base wallet for bounty payouts
- **AI-Powered Fixes** - Use Claude to analyze and fix issues automatically
- **Git Integration** - Auto-commit and create PRs
- **Beautiful CLI** - Rich terminal output with progress indicators

## Commands

### Authentication
- `ubounty login` - Log in with GitHub
- `ubounty logout` - Remove saved credentials
- `ubounty whoami` - Show current user and wallet status

### Wallet Management
- `ubounty wallet status` - Check wallet binding status
- `ubounty wallet bind <address>` - Bind wallet address for payouts

### Issue Management (Coming Soon)
- `ubounty fix-issue <number>` - Fix a GitHub issue with AI
- `ubounty list-issues` - List repository issues

### Setup
- `ubounty setup` - Interactive configuration guide
- `ubounty version` - Show version

## Documentation

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.
