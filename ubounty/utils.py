"""Utility functions for ubounty."""

import subprocess
from pathlib import Path
from typing import Optional


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def is_git_repo(path: Path = Path.cwd()) -> bool:
    """Check if the given path is a git repository."""
    return (path / ".git").exists()


def get_current_branch(path: Path = Path.cwd()) -> Optional[str]:
    """Get the current git branch name."""
    code, stdout, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    if code == 0:
        return stdout.strip()
    return None


def get_git_root(path: Path = Path.cwd()) -> Optional[Path]:
    """Get the root directory of the git repository."""
    code, stdout, _ = run_command(["git", "rev-parse", "--show-toplevel"], cwd=path)
    if code == 0:
        return Path(stdout.strip())
    return None
