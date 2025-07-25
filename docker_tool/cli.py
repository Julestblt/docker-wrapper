#!/usr/bin/env python3
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from .docker_client import DockerClient
from .version import __version__

app = typer.Typer(
    name="dtool",
    help="🐳 Docker operations made simple",
    add_completion=True,
    rich_markup_mode="rich",
    epilog="Made with ❤️ for developers who hate long Docker commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    },
    invoke_without_command=True,
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
    ctx: typer.Context,
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
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


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

@app.command()
def shell(
    container_id: str = typer.Argument(..., help="Container ID to exec into")
):
    """
    🐳 Spawn shell in a running container

    Examples:
        dtool shell e3f1d2
    """

    docker = check_docker_daemon()
    docker.spawn_shell(container_id=container_id)

@app.command()
def exec(
    container_id: str = typer.Argument(..., help="Container ID to exec into"),
    command: list[str] = typer.Argument(..., help="Command to run inside the container")
):
    """
    🐳 Execute a command in a running container

    Examples:
        dtool exec e3f1d2 id
        dtool exec e3f1d2 cat /etc/hostname
    """

    docker = check_docker_daemon()
    docker.exec_cmd(container_id=container_id, command=" ".join(command))

@app.command()
def logs(
    container_id: str = typer.Argument(..., help="Container ID or name to fetch logs for"),
    follow: bool = typer.Option(
        False, "--follow", "-f", help="Follow logs (tail -f style)"
    ),
):
    """
    📜 Fetch logs from a container

    Examples:
        dtool logs e3f1d2
        dtool logs e3f1d2 --follow
    """

    docker = check_docker_daemon()
    docker.fetch_logs(container_id=container_id, follow=follow)
    
    
@app.command()
def start(
    container_id: str = typer.Argument(..., help="Container ID or name to start")
):
    """
    ▶️ Start a stopped container

    Examples:
        dtool start e3f1d2
    """

    docker = check_docker_daemon()
    docker.start_container(container_id=container_id)
    
@app.command()
def stop(
    container_id: str = typer.Argument(..., help="Container ID or name to stop"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop the container")
):
    """
    ⏹️ Stop a running container

    Examples:
        dtool stop e3f1d2
    """

    docker = check_docker_daemon()
    docker.stop_container(container_id=container_id, force=force)
    
@app.command()
def restart(
    container_id: str = typer.Argument(..., help="Container ID or name to restart"),
    force: bool = typer.Option(False, "--force", "-f", help="Force restart the container")
):
    """
    🔄 Restart a running container

    Examples:
        dtool restart e3f1d2
    """

    docker = check_docker_daemon()
    docker.restart_container(container_id=container_id, force=force)
    
@app.command()
def rm(
    container_id: str = typer.Argument(..., help="Container ID or name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force remove the container")
):
    """
    🗑️ Remove a stopped container

    Examples:
        dtool rm e3f1d2
        dtool rm e3f1d2 --force
    """

    docker = check_docker_daemon()
    docker.remove_container(container_id=container_id, force=force)
    

if __name__ == "__main__":
    app()
