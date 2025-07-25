#!/usr/bin/env python3
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from lib.docker_client import DockerClient
from lib.version import __version__

app = typer.Typer(
    name="dtool",
    help="🐳 Docker operations made simple",
    add_completion=True,
    rich_markup_mode="rich",
    epilog="Made with ❤️ for developers who hate long Docker commands",
)

console = Console()

docker = DockerClient()


def check_docker_daemon():
    if not docker.is_daemon_running():
        console.print(
            Panel(
                "[bold red]Docker daemon is not running![/bold red]\n\n"
                "Please start Docker and try again.\n\n"
                "[dim]Common solutions:[/dim]\n"
                "• macOS: Start Docker Desktop\n"
                "• Linux: sudo systemctl start docker\n"
                "• WSL: sudo service docker start",
                title="⚠️  Docker Error",
                border_style="red"
            )
        )
        raise typer.Exit(1)
    return docker


def version_callback(value: bool):
    if value:
        console.print(
            f"[bold blue]Docker Tool[/bold blue] version {__version__}"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    🐳 Docker Tool - Smart Docker container management

    Run 'dtool COMMAND --help' for more information on a command.
    """
    pass


@app.command()
def ps(
    container: Optional[str] = typer.Argument(
        None, help="Container name or ID to filter"),
    all: bool = typer.Option(False, "--all", "-a", help="Show all containers"),
    regex: bool = typer.Option(
        False, "--regex", "-r", help="Use regex match")
):
    """
    📋 List containers

    Examples:
        dtool ps
        dtool ps --all
        dtool ps my-container
        dtool ps e3f1d2
    """

    docker = check_docker_daemon()

    if container:
        containers = docker.list_containers(
            all=all, filter=container, regex=regex)
    else:
        containers = docker.list_containers(all=all)

    docker.print_containers_rich(containers=containers)


if __name__ == "__main__":
    app()
