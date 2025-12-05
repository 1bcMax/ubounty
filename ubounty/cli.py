"""Main CLI entry point for ubounty."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing_extensions import Annotated

from ubounty import __version__
from ubounty.auth import GitHubAuth

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
    """Show current logged-in user information."""
    auth = GitHubAuth()

    if not auth.is_authenticated():
        console.print("[yellow]Not logged in[/yellow]")
        console.print("[dim]Run 'ubounty login' to authenticate[/dim]")
        raise typer.Exit(1)

    user_info = auth.get_user_info()
    if not user_info:
        console.print("[red]Error: Could not retrieve user information[/red]")
        raise typer.Exit(1)

    table = Table(title="Current User", show_header=False, box=None)
    table.add_column("Field", style="bold blue")
    table.add_column("Value", style="green")

    table.add_row("Username", f"@{user_info.get('login', 'N/A')}")
    if user_info.get("name"):
        table.add_row("Name", user_info["name"])
    if user_info.get("email"):
        table.add_row("Email", user_info["email"])

    console.print()
    console.print(table)
    console.print()


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
        "\n[dim]For now, create a .env file with:[/dim]"
        "\n  ANTHROPIC_API_KEY=your_anthropic_key"
    )
    console.print(
        "\n[dim]Get your API key at: https://console.anthropic.com/[/dim]\n"
    )


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
