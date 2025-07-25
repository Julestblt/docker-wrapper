import re
import sys
import docker
from typing import List, Dict
from docker.errors import DockerException
from rich.console import Console
from rich.table import Table
import os

console = Console()


class DockerClient:
    def __init__(self, capture: bool = False):
        self.capture = capture

    def is_daemon_running(self) -> bool:
        """
        Check if the Docker daemon is running.
        Returns True if running, False otherwise.
        """
        try:
            client = docker.from_env()
            client.ping()
            return True
        except DockerException:
            return False

    def list_containers(self, all: bool = True,
                        filter: str = False, regex: bool = True) -> List[Dict]:
        try:
            client = docker.from_env()
            if filter:
                containers = client.containers.list(all=all)
                if not regex:
                    return [c for c in containers if c.name == filter or c.id == filter or c.id.startswith(filter)]
                return [c for c in containers if re.search(filter, c.name, re.IGNORECASE) or re.search(filter, c.id, re.IGNORECASE)]
            else:
                return client.containers.list(all=all)

        except DockerException as e:
            if self.capture and e.stderr:
                print(e.stderr, file=sys.stderr)
            raise

    def print_containers_rich(self, containers: List):
        if not containers:
            console.print(
                "[bold yellow]No containers found.[/bold yellow]"
            )
            return

        table = Table(title="Docker Containers",
                      show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Name", style="green")
        table.add_column("Image", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Ports", style="dim")

        for container in containers:
            container_id = container.short_id
            name = container.name
            image = (container.image.tags[0] if container.image.tags
                     else container.image.id[:12])
            status = container.status

            ports = []
            if container.ports:
                for container_port, host_bindings in container.ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            host_port = binding['HostPort']
                            port_mapping = f"{host_port}:{container_port}"
                            ports.append(port_mapping)
                    else:
                        ports.append(container_port)
            ports_str = ", ".join(ports) if ports else ""

            # Couleur du status
            status_color = "green" if status == "running" else "red"

            table.add_row(
                container_id,
                name,
                image,
                f"[{status_color}]{status}[/{status_color}]",
                ports_str
            )

        console.print(table)
        
    def spawn_shell(self, container_id: str):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container.status != 'running':
                raise DockerException(f"Container {container_id} is not running.")
            
            console.print(f"\n[bold green]Entering shell in container[/bold green] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]\n")
            
            cmd = [
                "docker", "exec", "-it", 
                container_id, 
                "/bin/sh"
            ]
            
            os.execvp("docker", cmd)
            
        except DockerException as e:
            if self.capture and e.stderr:
                print(e.stderr, file=sys.stderr)
            raise
        
    def exec_cmd(self, container_id: str, command: List[str]):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container.status != 'running':
                raise DockerException(f"Container {container_id} is not running.")
            
            exec_instance = client.api.exec_create(
                container_id, command, tty=True, stdin=True
            )
            output = client.api.exec_start(exec_instance['Id'], stream=True)
            
            for line in output:
                print(line.decode('utf-8'), end='')
                if self.capture:
                    self.captured_output.append(line.decode('utf-8'))
        except DockerException as e:
            if self.capture and e.stderr:
                print(e.stderr, file=sys.stderr)
            raise
