import questionary
from rich.console import Console
from rich.panel import Panel
from typing import List
from .docker_client import DockerClient

console = Console()


class DockerWizard:
    def __init__(self, docker_client: DockerClient):
        self.docker = docker_client
        self.style = questionary.Style(
            [
                ("qmark", "fg:#673ab7 bold"),
                ("question", "bold"),
                ("answer", "fg:#f44336 bold"),
                ("pointer", "fg:#673ab7 bold"),
                ("highlighted", "fg:#673ab7 bold"),
                ("selected", "fg:#cc5454"),
                ("separator", "fg:#cc5454"),
                ("instruction", "fg:#abb2bf"),
                ("text", "fg:#61afef"),
            ]
        )

    def run(self):
        containers = self.docker.list_containers(all=True)

        if not containers:
            console.print("[red]No containers found![/red]")
            return

        self.container_selection_wizard(containers)

    def container_selection_wizard(self, containers: List):
        while True:
            choices = []
            for c in containers:
                status_emoji = "🟢" if c.status == "running" else "🔴"
                image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
                choices.append(
                    {
                        "name": f"{status_emoji} {c.name} ({c.short_id}) - {image_name}",
                        "value": c,
                    }
                )

            choices.append({"name": "❌ Exit", "value": None})

            result = questionary.select(
                "Select a container to manage:", choices=choices, style=self.style
            ).ask()

            if result is None or result == "❌ Exit":
                console.print("[yellow]Exiting wizard...[/yellow]")
                break

            selected_container = next(
                (choice["value"] for choice in choices if choice["name"] == result),
                None,
            )

            if selected_container:
                self.manage_container(selected_container)

            containers = self.docker.list_containers(all=True)

    def manage_container(self, container):
        while True:
            console.clear()
            console.print(
                Panel(
                    f"[bold]Container:[/bold] {container.name}\n"
                    f"[bold]ID:[/bold] {container.short_id}\n"
                    f"[bold]Image:[/bold] {container.image.tags[0] if container.image.tags else container.image.id[:12]}\n"
                    f"[bold]Status:[/bold] [{'green' if container.status == 'running' else 'red'}]{container.status}[/{'green' if container.status == 'running' else 'red'}]",
                    title="📦 Container Details",
                    border_style="blue",
                )
            )

            actions = []

            if container.status == "running":
                actions.extend(
                    [
                        {"name": "🐚 Open shell", "value": "shell"},
                        {"name": "⚡ Execute command", "value": "exec"},
                        {"name": "📜 View logs", "value": "logs"},
                        {"name": "🔄 Restart", "value": "restart"},
                        {"name": "🛑 Stop", "value": "stop"},
                    ]
                )
            else:
                actions.append({"name": "▶️  Start", "value": "start"})
                actions.append({"name": "📜 View logs", "value": "logs"})

            actions.extend(
                [
                    {"name": "🗑️  Remove", "value": "remove"},
                    {"name": "🔙 Back to container list", "value": "back"},
                ]
            )

            action = questionary.select(
                "Choose an action:", choices=actions, style=self.style
            ).ask()

            if action == "back":
                break

            self.execute_action(container, action)

            container.reload()

    def execute_action(self, container, action: str):
        container_id = container.id

        if action == "shell":
            shell_choices = [
                {"name": "/bin/bash", "value": "/bin/bash"},
                {"name": "/bin/sh", "value": "/bin/sh"},
                {"name": "/bin/zsh", "value": "/bin/zsh"},
                {"name": "Custom...", "value": "custom"},
            ]

            shell = questionary.select(
                "Select shell type:", choices=shell_choices, style=self.style
            ).ask()

            if shell == "custom":
                shell = questionary.text(
                    "Enter shell path:", default="/bin/bash", style=self.style
                ).ask()

            if shell:
                console.print(
                    f"\n[green]Opening {shell} in {container.name}...[/green]\n"
                )
                self.docker._spawn_shell_in_container(container, shell)
                input("\nPress Enter to continue...")

        elif action == "exec":
            command = questionary.text(
                "Enter command to execute:", style=self.style
            ).ask()

            if command:
                console.print(f"\n[green]Executing: {command}[/green]\n")
                self.docker._exec_cmd_in_container(container, command)
                input("\nPress Enter to continue...")

        elif action == "logs":
            follow = questionary.confirm(
                "Follow log output?", default=True, style=self.style
            ).ask()

            console.print("\n[green]Showing logs (Ctrl+C to stop)...[/green]\n")
            try:
                self.docker._fetch_logs_from_container(container, follow=follow)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs[/yellow]")
            input("\nPress Enter to continue...")

        elif action == "stop":
            force = questionary.confirm(
                f"Stop container {container.name}?", default=False, style=self.style
            ).ask()

            if force:
                self.docker.stop_container(container_id)
                input("\nPress Enter to continue...")

        elif action == "start":
            self.docker.start_container(container_id)
            input("\nPress Enter to continue...")

        elif action == "restart":
            self.docker.restart_container(container_id)
            input("\nPress Enter to continue...")

        elif action == "remove":
            if container.status == "running":
                force = questionary.confirm(
                    f"⚠️  Container is running! Force remove {container.name}?",
                    default=False,
                    style=self.style,
                ).ask()

                if force:
                    self.docker.remove_container(container_id, force=True)
                    input("\nPress Enter to continue...")
                    return
            else:
                confirm = questionary.confirm(
                    f"Remove container {container.name}?",
                    default=False,
                    style=self.style,
                ).ask()

                if confirm:
                    self.docker.remove_container(container_id)
                    input("\nPress Enter to continue...")
                    return
