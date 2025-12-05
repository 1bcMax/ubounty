"""AI agent for fixing GitHub issues."""

from typing import Optional

from anthropic import Anthropic
from github.Issue import Issue
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ubounty.config import Settings

console = Console()


class IssueFixerAgent:
    """AI agent that fixes GitHub issues using Claude."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the agent with settings."""
        self.settings = settings
        if not settings.validate_anthropic_key():
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or run 'ubounty setup'"
            )
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def analyze_issue(self, issue: Issue) -> dict[str, str]:
        """Analyze a GitHub issue and create a plan to fix it."""
        console.print("\n[bold blue]Analyzing issue...[/bold blue]")

        issue_context = self._format_issue_context(issue)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Thinking...", total=None)

            response = self.client.messages.create(
                model=self.settings.model,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are an expert software engineer tasked with analyzing and fixing GitHub issues.

Issue Context:
{issue_context}

Please analyze this issue and provide:
1. A summary of what needs to be done
2. Files that likely need to be modified
3. A step-by-step plan to fix the issue
4. Any potential challenges or considerations

Format your response as a clear, structured plan.""",
                    }
                ],
            )

        analysis = response.content[0].text
        console.print("\n[bold green]Analysis Complete:[/bold green]")
        console.print(Markdown(analysis))

        return {"analysis": analysis, "issue_context": issue_context}

    def generate_fix(
        self, issue: Issue, codebase_context: Optional[str] = None
    ) -> dict[str, str]:
        """Generate code to fix the issue."""
        console.print("\n[bold blue]Generating fix...[/bold blue]")

        issue_context = self._format_issue_context(issue)

        prompt = f"""You are an expert software engineer tasked with fixing GitHub issues.

Issue Context:
{issue_context}
"""

        if codebase_context:
            prompt += f"\n\nCodebase Context:\n{codebase_context}\n"

        prompt += """
Please provide:
1. The specific code changes needed to fix this issue
2. Files to create or modify with exact content
3. A commit message for these changes
4. A description for a pull request

Format your response clearly with sections for each part."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Generating fix...", total=None)

            response = self.client.messages.create(
                model=self.settings.model,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

        fix_plan = response.content[0].text
        console.print("\n[bold green]Fix Generated:[/bold green]")
        console.print(Markdown(fix_plan))

        return {"fix_plan": fix_plan, "issue_context": issue_context}

    def _format_issue_context(self, issue: Issue) -> str:
        """Format issue information for the AI."""
        context = f"""
Title: {issue.title}
Number: #{issue.number}
State: {issue.state}
Created: {issue.created_at}
Author: {issue.user.login}

Description:
{issue.body or 'No description provided'}
"""

        if issue.labels:
            labels = ", ".join([label.name for label in issue.labels])
            context += f"\nLabels: {labels}"

        if issue.comments > 0:
            context += f"\n\nComments ({issue.comments}):\n"
            for comment in issue.get_comments()[:5]:  # Limit to first 5 comments
                context += f"\n---\n{comment.user.login} at {comment.created_at}:\n{comment.body}\n"

        return context
