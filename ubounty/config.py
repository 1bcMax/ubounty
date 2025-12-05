"""Configuration management for ubounty."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GitHub settings
    github_token: Optional[str] = Field(default=None, description="GitHub personal access token")

    # Anthropic API settings
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key for Claude"
    )

    # CLI behavior settings
    default_base_branch: str = Field(default="main", description="Default base branch name")
    auto_commit: bool = Field(default=False, description="Automatically commit changes")
    auto_pr: bool = Field(default=False, description="Automatically create pull requests")

    # AI model settings
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    max_tokens: int = Field(default=8192, description="Maximum tokens for AI responses")
    temperature: float = Field(default=0.7, description="Temperature for AI responses")

    # ubounty API settings
    ubounty_api_url: str = Field(
        default="https://ubounty.ai", description="ubounty API base URL"
    )

    def validate_github_token(self) -> bool:
        """Check if GitHub token is set."""
        return self.github_token is not None and len(self.github_token) > 0

    def validate_anthropic_key(self) -> bool:
        """Check if Anthropic API key is set."""
        return self.anthropic_api_key is not None and len(self.anthropic_api_key) > 0


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_project_root() -> Path:
    """Get the project root directory (where .git is located)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_repo_name_from_git() -> Optional[str]:
    """Extract repo name from git remote URL."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()

        # Parse GitHub URL (supports both HTTPS and SSH)
        # HTTPS: https://github.com/owner/repo.git
        # SSH: git@github.com:owner/repo.git
        if "github.com" in url:
            if url.startswith("git@"):
                # SSH format
                repo = url.split(":")[-1].replace(".git", "")
            else:
                # HTTPS format
                repo = "/".join(url.split("/")[-2:]).replace(".git", "")
            return repo
    except Exception:
        pass
    return None
