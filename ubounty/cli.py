"""Main CLI entry point for ubounty."""

import re
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing_extensions import Annotated

from ubounty import __version__
from ubounty.api_client import UbountyAPIClient
from ubounty.auth import GitHubAuth
from ubounty.config import get_settings

app = typer.Typer(
    name="ubounty",
    help="Enable maintainers to clear their backlog with one command",
    add_completion=True,
)
console = Console()


@app.command()
def version() -> None:
    """Show the version of ubounty."""
    console.print(f"[bold blue]ubounty[/bold blue] version {__version__}")


@app.command()
def fix_issue(
    issue_number: Annotated[int, typer.Argument(help="GitHub issue number to fix")],
    repo: Annotated[
        str, typer.Option("--repo", "-r", help="Repository in format owner/repo")
    ] = "",
    auto_commit: Annotated[
        bool, typer.Option("--auto-commit", "-c", help="Automatically commit changes")
    ] = False,
    auto_pr: Annotated[
        bool, typer.Option("--auto-pr", "-p", help="Automatically create a pull request")
    ] = False,
) -> None:
    """Fix a GitHub issue automatically using AI."""
    console.print(
        Panel.fit(
            f"[bold green]Fixing issue #{issue_number}[/bold green]",
            title="ubounty",
            border_style="blue",
        )
    )

    if not repo:
        console.print("[yellow]No repo specified. Detecting from current directory...[/yellow]")
        # TODO: Implement repo detection from git remote

    console.print(f"[dim]Repository: {repo or 'auto-detect'}[/dim]")
    console.print(f"[dim]Auto-commit: {auto_commit}[/dim]")
    console.print(f"[dim]Auto-PR: {auto_pr}[/dim]")

    # TODO: Implement the actual fix logic
    console.print("\n[yellow]Implementation coming soon![/yellow]")


@app.command()
def list_issues(
    repo: Annotated[
        str, typer.Option("--repo", "-r", help="Repository in format owner/repo")
    ] = "",
    state: Annotated[
        str, typer.Option("--state", "-s", help="Issue state: open, closed, or all")
    ] = "open",
    labels: Annotated[
        str, typer.Option("--labels", "-l", help="Comma-separated list of labels")
    ] = "",
) -> None:
    """List GitHub issues in a repository."""
    console.print(
        Panel.fit(
            "[bold blue]Listing issues[/bold blue]",
            title="ubounty",
            border_style="blue",
        )
    )

    if not repo:
        console.print("[yellow]No repo specified. Detecting from current directory...[/yellow]")

    # TODO: Implement issue listing
    console.print("\n[yellow]Implementation coming soon![/yellow]")


@app.command()
def login() -> None:
    """Log in to GitHub using device flow authentication."""
    auth = GitHubAuth()

    if auth.is_authenticated():
        user_info = auth.get_user_info()
        if user_info:
            console.print(
                f"[yellow]Already logged in as @{user_info.get('login')}[/yellow]"
            )
            console.print("[dim]Run 'ubounty logout' to switch accounts[/dim]")
            return

    success = auth.login()
    if not success:
        raise typer.Exit(1)


@app.command()
def logout() -> None:
    """Log out and remove saved credentials."""
    auth = GitHubAuth()
    success = auth.logout()
    if not success:
        raise typer.Exit(1)


@app.command()
def whoami() -> None:
    """Show current user information and wallet status."""
    try:
        settings = get_settings()
        client = UbountyAPIClient(api_url=settings.ubounty_api_url)

        if not client.is_authenticated():
            console.print("[yellow]Not logged in[/yellow]")
            console.print("[dim]Run 'ubounty login' to authenticate[/dim]")
            raise typer.Exit(1)

        # Fetch user settings from API
        user_settings = client.get_user_settings()

        # Display user info
        table = Table(title="Current User", show_header=False, box=None)
        table.add_column("Field", style="bold blue")
        table.add_column("Value", style="green")

        table.add_row("Username", f"@{user_settings['github_username']}")
        if user_settings.get("name"):
            table.add_row("Name", user_settings["name"])
        if user_settings.get("email"):
            table.add_row("Email", user_settings["email"])

        console.print()
        console.print(table)

        # Display wallet info
        if user_settings.get("wallet"):
            wallet = user_settings["wallet"]
            wallet_table = Table(title="Wallet", show_header=False, box=None)
            wallet_table.add_column("Field", style="bold blue")
            wallet_table.add_column("Value", style="green")

            if wallet["status"] == "bound":
                wallet_table.add_row("Status", "✓ Bound")
                wallet_table.add_row(
                    "Network", f"{wallet['network']} (Chain ID: {wallet['chain_id']})"
                )
                wallet_table.add_row("Address", wallet["address"])
            else:
                wallet_table.add_row("Status", "⚠ Not bound")

            console.print()
            console.print(wallet_table)

            if wallet["status"] != "bound":
                console.print("\n[yellow]Tip:[/yellow] Bind your wallet at https://ubounty.ai/settings")

        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


# Wallet command group
wallet_app = typer.Typer(help="Manage your wallet")
app.add_typer(wallet_app, name="wallet")


@wallet_app.command("status")
def wallet_status() -> None:
    """Show wallet status."""
    try:
        settings = get_settings()
        client = UbountyAPIClient(api_url=settings.ubounty_api_url)

        if not client.is_authenticated():
            console.print("[yellow]Not logged in[/yellow]")
            console.print("[dim]Run 'ubounty login' to authenticate[/dim]")
            raise typer.Exit(1)

        user_settings = client.get_user_settings()

        if not user_settings.get("wallet") or user_settings["wallet"]["status"] != "bound":
            console.print("[yellow]⚠ No wallet address bound[/yellow]")
            console.print("\n[dim]Bind your wallet at:[/dim] https://ubounty.ai/settings")
            console.print("[dim]Or run:[/dim] ubounty wallet bind <address>")
            raise typer.Exit(1)

        wallet = user_settings["wallet"]

        console.print("\n[bold green]✓ Wallet Bound[/bold green]")
        console.print(
            f"\n[bold]Network:[/bold] {wallet['network']} (Chain ID: {wallet['chain_id']})"
        )
        console.print(f"[bold]Address:[/bold] {wallet['address']}")
        if wallet.get("bound_at"):
            console.print(f"[dim]Bound at:[/dim] {wallet['bound_at']}")
        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@wallet_app.command("bind")
def wallet_bind(
    address: Annotated[str, typer.Argument(help="Wallet address (0x...)")],
) -> None:
    """Bind a wallet address."""
    console.print(
        Panel.fit(
            "[bold blue]Binding Wallet[/bold blue]",
            subtitle=f"Address: {address}",
            border_style="blue",
        )
    )

    # Client-side validation
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        console.print("[bold red]Error:[/bold red] Invalid address format")
        console.print("[dim]Address must be 0x followed by 40 hex characters[/dim]")
        raise typer.Exit(1)

    try:
        settings = get_settings()
        client = UbountyAPIClient(api_url=settings.ubounty_api_url)

        if not client.is_authenticated():
            console.print("[yellow]Not logged in[/yellow]")
            console.print("[dim]Run 'ubounty login' to authenticate[/dim]")
            raise typer.Exit(1)

        result = client.update_wallet(address)

        console.print("\n[bold green]✓ Wallet address successfully bound![/bold green]")
        console.print(f"\n[bold]Network:[/bold] {result['wallet']['network']}")
        console.print(f"[bold]Address:[/bold] {result['wallet']['address']}")
        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Alternative:[/yellow] Bind your wallet on the website:")
        console.print("→ https://ubounty.ai/settings")
        raise typer.Exit(1)


@app.command()
def setup() -> None:
    """Set up ubounty configuration (GitHub token, Anthropic API key, etc.)."""
    console.print(
        Panel.fit(
            "[bold blue]Setting up ubounty[/bold blue]",
            title="ubounty",
            border_style="blue",
        )
    )

    console.print("\n[bold]This will help you configure ubounty.[/bold]\n")

    # Step 1: GitHub authentication
    auth = GitHubAuth()
    if not auth.is_authenticated():
        console.print("[bold]Step 1: GitHub Authentication[/bold]")
        if typer.confirm("Would you like to log in to GitHub now?", default=True):
            auth.login()
    else:
        user_info = auth.get_user_info()
        console.print(
            f"[green]✓ Already logged in to GitHub as @{user_info.get('login')}[/green]"
        )

    # Step 2: Anthropic API key
    console.print("\n[bold]Step 2: Anthropic API Key[/bold]")
    console.print(
        "\n[dim]Create a .env file with:[/dim]"
        "\n  ANTHROPIC_API_KEY=your_anthropic_key"
    )
    console.print("\n[dim]Get your API key at: https://console.anthropic.com/[/dim]\n")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
