"""API client for communicating with ubounty.ai backend."""

import requests
from typing import Any, Optional

from rich.console import Console

from ubounty import __version__
from ubounty.auth import GitHubAuth

console = Console()


class UbountyAPIClient:
    """Client for interacting with ubounty.ai API."""

    def __init__(self, api_url: str = "https://ubounty.ai") -> None:
        """
        Initialize API client.

        Args:
            api_url: Base URL for ubounty.ai API (default: https://ubounty.ai)
        """
        self.base_url = api_url.rstrip("/")
        self.auth = GitHubAuth()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has GitHub token)."""
        return self.auth.is_authenticated()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        github_token = self.auth.get_token()
        if not github_token:
            raise ValueError("Not logged in. Run 'ubounty login' first")

        return {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
            "User-Agent": f"ubounty-cli/{__version__}",
        }

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and errors.

        Args:
            response: HTTP response from API

        Returns:
            Parsed JSON response

        Raises:
            ValueError: For authentication or general API errors
        """
        if response.status_code == 401:
            try:
                error_data = response.json()
                console.print(f"[bold red]Error:[/bold red] {error_data.get('error')}")
                console.print(f"[dim]{error_data.get('message')}[/dim]")
            except Exception:
                console.print(f"[bold red]Error:[/bold red] Authentication failed")
            raise ValueError("Authentication failed")

        elif response.status_code >= 400:
            try:
                error_data = response.json()
                console.print(
                    f"[bold red]Error:[/bold red] {error_data.get('error', 'Unknown error')}"
                )
            except Exception:
                console.print(f"[bold red]Error:[/bold red] HTTP {response.status_code}")
            raise ValueError(f"API error: {response.status_code}")

        return response.json()

    def get_user_settings(self) -> dict[str, Any]:
        """
        Get user settings including wallet address.

        Returns:
            User settings including wallet information

        Raises:
            ValueError: If authentication fails
        """
        response = requests.get(
            f"{self.base_url}/api/users/me/settings", headers=self._get_headers(), timeout=10
        )
        return self._handle_response(response)

    def update_wallet(self, wallet_address: str) -> dict[str, Any]:
        """
        Update user's wallet address.

        Args:
            wallet_address: Ethereum wallet address (0x...)

        Returns:
            Updated wallet information

        Raises:
            ValueError: If address is invalid or update fails
        """
        response = requests.post(
            f"{self.base_url}/api/users/me/settings",
            headers=self._get_headers(),
            json={"wallet_address": wallet_address},
            timeout=10,
        )
        return self._handle_response(response)
