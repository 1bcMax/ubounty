# ubounty

Enable maintainers to clear their backlog with one command. Turn "I'll fix this someday" into "Done in 5 minutes."

## Quick Start

```bash
# Install
pip install -e .

# Log in to GitHub
ubounty login

# Fix an issue
ubounty fix-issue 42

# List issues
ubounty list-issues
```

## Features

- **Easy Authentication** - Log in with `ubounty login` using GitHub device flow
- **AI-Powered Fixes** - Use Claude to analyze and fix issues automatically
- **Git Integration** - Auto-commit and create PRs
- **Beautiful CLI** - Rich terminal output with progress indicators

## Commands

- `ubounty login` - Authenticate with GitHub
- `ubounty logout` - Remove saved credentials
- `ubounty whoami` - Show current user
- `ubounty fix-issue <number>` - Fix a GitHub issue with AI
- `ubounty list-issues` - List repository issues
- `ubounty setup` - Interactive configuration
- `ubounty version` - Show version

## Documentation

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.
