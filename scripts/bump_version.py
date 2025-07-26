import re
from pathlib import Path
import subprocess

VERSION_FILE = Path("docker_tool/version.py")
PYPROJECT_FILE = Path("pyproject.toml")

def bump_patch(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"

def update_version_file(new_version: str):
    content = VERSION_FILE.read_text()
    content = re.sub(r'__version__ = "(.+?)"', f'__version__ = "{new_version}"', content)
    VERSION_FILE.write_text(content)

def update_pyproject_file(new_version: str):
    content = PYPROJECT_FILE.read_text()
    content = re.sub(r'version = "(.+?)"', f'version = "{new_version}"', content)
    PYPROJECT_FILE.write_text(content)

def get_current_version() -> str:
    match = re.search(r'__version__ = "(.+?)"', VERSION_FILE.read_text())
    return match.group(1)

def git_commit_and_tag(new_version: str):
    subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
    subprocess.run(["git", "add", "pyproject.toml", str(VERSION_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version} [CI]"], check=True)
    subprocess.run(["git", "tag", f"v{new_version}"], check=True)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)

if __name__ == "__main__":
    current = get_current_version()
    new_version = bump_patch(current)
    update_version_file(new_version)
    update_pyproject_file(new_version)
    git_commit_and_tag(new_version)
    print(f"Bumped version: {current} → {new_version}")
