"""GitHub API client for ubounty."""

import os
from typing import Optional

from github import Github, GithubException
from github.Issue import Issue
from github.Repository import Repository
from rich.console import Console

from ubounty.auth import GitHubAuth

console = Console()


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize GitHub client with optional token."""
        # Try token from parameter, then auth, then environment variable
        if token:
            self.token = token
        else:
            auth = GitHubAuth()
            self.token = auth.get_token() or os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise ValueError(
                "GitHub token not found. Run 'ubounty login' or set GITHUB_TOKEN "
                "environment variable"
            )
        self.client = Github(self.token)

    def get_repository(self, repo_name: str) -> Repository:
        """Get a repository by name (format: owner/repo)."""
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to access repository: {e}")
            raise

    def get_issue(self, repo_name: str, issue_number: int) -> Issue:
        """Get a specific issue from a repository."""
        repo = self.get_repository(repo_name)
        try:
            return repo.get_issue(issue_number)
        except GithubException as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to fetch issue #{issue_number}: {e}"
            )
            raise

    def list_issues(
        self,
        repo_name: str,
        state: str = "open",
        labels: Optional[list[str]] = None,
    ) -> list[Issue]:
        """List issues from a repository."""
        repo = self.get_repository(repo_name)
        try:
            issues = repo.get_issues(state=state, labels=labels or [])
            return list(issues)
        except GithubException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to list issues: {e}")
            raise

    def create_branch(self, repo_name: str, branch_name: str, base_branch: str = "main") -> None:
        """Create a new branch in the repository."""
        repo = self.get_repository(repo_name)
        try:
            base = repo.get_branch(base_branch)
            repo.create_git_ref(f"refs/heads/{branch_name}", base.commit.sha)
            console.print(f"[green]Created branch:[/green] {branch_name}")
        except GithubException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to create branch: {e}")
            raise

    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> str:
        """Create a pull request."""
        repo = self.get_repository(repo_name)
        try:
            pr = repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
            console.print(f"[green]Created pull request:[/green] {pr.html_url}")
            return pr.html_url
        except GithubException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to create pull request: {e}")
            raise

    def add_comment_to_issue(self, repo_name: str, issue_number: int, comment: str) -> None:
        """Add a comment to an issue."""
        issue = self.get_issue(repo_name, issue_number)
        try:
            issue.create_comment(comment)
            console.print(f"[green]Added comment to issue #{issue_number}[/green]")
        except GithubException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to add comment: {e}")
            raise
