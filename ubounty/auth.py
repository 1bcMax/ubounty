"""GitHub authentication and credential management."""

import json
import time
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

GITHUB_CLIENT_ID = "Iv1.b507a08c87ecfe98"  # Public GitHub OAuth App for CLI tools
CONFIG_DIR = Path.home() / ".config" / "ubounty"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


class GitHubAuth:
    """Handle GitHub authentication via device flow."""

    def __init__(self) -> None:
        """Initialize auth handler."""
        self.config_dir = CONFIG_DIR
        self.credentials_file = CREDENTIALS_FILE

    def login(self) -> bool:
        """Authenticate with GitHub using device flow."""
        console.print(
            Panel.fit(
                "[bold blue]GitHub Login[/bold blue]",
                subtitle="Using device flow authentication",
                border_style="blue",
            )
        )

        try:
            # Step 1: Request device code
            device_code_response = requests.post(
                "https://github.com/login/device/code",
                headers={"Accept": "application/json"},
                data={"client_id": GITHUB_CLIENT_ID, "scope": "repo workflow"},
                timeout=10,
            )
            device_code_response.raise_for_status()
            device_data = device_code_response.json()

            user_code = device_data["user_code"]
            device_code = device_data["device_code"]
            verification_uri = device_data["verification_uri"]
            interval = device_data.get("interval", 5)

            # Step 2: Show user code and instructions
            console.print("\n[bold green]Step 1:[/bold green] Copy your code:")
            console.print(
                Panel.fit(
                    f"[bold yellow]{user_code}[/bold yellow]",
                    border_style="yellow",
                )
            )

            console.print(
                f"\n[bold green]Step 2:[/bold green] Open this URL in your browser:\n"
                f"  [link={verification_uri}]{verification_uri}[/link]\n"
            )

            console.print(
                "[bold green]Step 3:[/bold green] Paste the code and authorize ubounty\n"
            )

            if not Confirm.ask("Ready to continue?", default=True):
                console.print("[yellow]Login cancelled[/yellow]")
                return False

            # Step 3: Poll for access token
            console.print("[dim]Waiting for authorization...[/dim]")

            max_attempts = 60  # 5 minutes timeout
            for _ in range(max_attempts):
                time.sleep(interval)

                token_response = requests.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    },
                    timeout=10,
                )

                token_data = token_response.json()

                if "access_token" in token_data:
                    access_token = token_data["access_token"]

                    # Get user info
                    user_info = self._get_user_info(access_token)

                    # Save credentials
                    self._save_credentials(access_token, user_info)

                    console.print(
                        f"\n[bold green]✓ Successfully logged in as "
                        f"@{user_info.get('login', 'unknown')}![/bold green]"
                    )
                    return True

                elif token_data.get("error") == "authorization_pending":
                    continue
                elif token_data.get("error") == "slow_down":
                    interval += 5
                    continue
                elif token_data.get("error") == "expired_token":
                    console.print("[bold red]Error:[/bold red] Device code expired")
                    return False
                elif token_data.get("error") == "access_denied":
                    console.print("[yellow]Authorization denied[/yellow]")
                    return False
                else:
                    console.print(
                        f"[bold red]Error:[/bold red] {token_data.get('error', 'Unknown error')}"
                    )
                    return False

            console.print("[bold red]Error:[/bold red] Authentication timeout")
            return False

        except requests.RequestException as e:
            console.print(f"[bold red]Error:[/bold red] Network error: {e}")
            return False
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return False

    def logout(self) -> bool:
        """Remove saved credentials."""
        if not self.credentials_file.exists():
            console.print("[yellow]No saved credentials found[/yellow]")
            return False

        if Confirm.ask("Are you sure you want to logout?", default=True):
            self.credentials_file.unlink()
            console.print("[green]✓ Logged out successfully[/green]")
            return True

        return False

    def get_token(self) -> Optional[str]:
        """Get saved GitHub token."""
        if not self.credentials_file.exists():
            return None

        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
                return data.get("token")
        except Exception:
            return None

    def get_user_info(self) -> Optional[dict]:
        """Get saved user info."""
        if not self.credentials_file.exists():
            return None

        try:
            with open(self.credentials_file, "r") as f:
                data = json.load(f)
                return data.get("user")
        except Exception:
            return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.credentials_file.exists() and self.get_token() is not None

    def _get_user_info(self, token: str) -> dict:
        """Fetch user info from GitHub API."""
        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _save_credentials(self, token: str, user_info: dict) -> None:
        """Save credentials to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        credentials = {
            "token": token,
            "user": {
                "login": user_info.get("login"),
                "name": user_info.get("name"),
                "email": user_info.get("email"),
                "avatar_url": user_info.get("avatar_url"),
            },
        }

        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)

        # Set restrictive permissions
        self.credentials_file.chmod(0o600)
