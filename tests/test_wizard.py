import pytest
import unittest.mock as mock
from docker_tool.wizard import DockerWizard
from docker_tool.docker_client import DockerClient


class TestDockerWizard:
    """Tests for the DockerWizard class"""

    @pytest.fixture
    def mock_docker_client(self):
        """Create a mock DockerClient for testing"""
        client = mock.Mock(spec=DockerClient)
        return client

    @pytest.fixture
    def wizard(self, mock_docker_client):
        """Create a DockerWizard instance for testing"""
        return DockerWizard(mock_docker_client)

    @pytest.fixture
    def mock_container(self):
        """Create a mock container for testing"""
        container = mock.Mock()
        container.id = "test123456789"
        container.short_id = "test123"
        container.name = "test-container"
        container.status = "running"
        container.image.tags = ["nginx:latest"]
        return container

    def test_wizard_init(self, mock_docker_client):
        """Test wizard initialization"""
        wizard = DockerWizard(mock_docker_client)
        assert wizard.docker == mock_docker_client
        assert wizard.style is not None

    def test_run_no_containers(self, wizard, mock_docker_client):
        """Test wizard run when no containers exist"""
        mock_docker_client.list_containers.return_value = []

        with mock.patch("docker_tool.wizard.console") as mock_console:
            wizard.run()
            mock_console.print.assert_called_with("[red]No containers found![/red]")

    def test_run_with_containers(self, wizard, mock_docker_client, mock_container):
        """Test wizard run with containers"""
        mock_docker_client.list_containers.return_value = [mock_container]

        with mock.patch.object(wizard, "container_selection_wizard") as mock_selection:
            wizard.run()
            mock_selection.assert_called_once_with([mock_container])

    @mock.patch("docker_tool.wizard.questionary")
    def test_container_selection_wizard_exit(
        self, mock_questionary, wizard, mock_docker_client, mock_container
    ):
        """Test container selection wizard with exit selection"""
        mock_docker_client.list_containers.return_value = [mock_container]

        mock_select = mock.Mock()
        mock_select.ask.return_value = "❌ Exit"
        mock_questionary.select.return_value = mock_select

        with mock.patch("docker_tool.wizard.console") as mock_console:
            wizard.container_selection_wizard([mock_container])
            mock_console.print.assert_called_with("[yellow]Exiting wizard...[/yellow]")

    @mock.patch("docker_tool.wizard.questionary")
    def test_container_selection_wizard_select_container(
        self, mock_questionary, wizard, mock_docker_client, mock_container
    ):
        """Test container selection wizard with container selection"""
        mock_docker_client.list_containers.return_value = [mock_container]

        mock_select = mock.Mock()
        container_choice = "🟢 test-container (test123) - nginx:latest"
        mock_select.ask.side_effect = [container_choice, "❌ Exit"]
        mock_questionary.select.return_value = mock_select

        with mock.patch.object(wizard, "manage_container") as mock_manage:
            with mock.patch("docker_tool.wizard.console"):
                wizard.container_selection_wizard([mock_container])
                mock_manage.assert_called_once_with(mock_container)

    @mock.patch("docker_tool.wizard.questionary")
    def test_manage_container_back_action(self, mock_questionary, wizard, mock_container):
        """Test manage container with back action"""
        mock_select = mock.Mock()
        mock_select.ask.return_value = "back"
        mock_questionary.select.return_value = mock_select

        with mock.patch("docker_tool.wizard.console"):
            wizard.manage_container(mock_container)

    @mock.patch("docker_tool.wizard.questionary")
    def test_manage_container_shell_action(
        self, mock_questionary, wizard, mock_container, mock_docker_client
    ):
        """Test manage container with shell action"""
        wizard.docker = mock_docker_client

        mock_select = mock.Mock()
        mock_select.ask.side_effect = ["shell", "back"]  # Action, then back
        mock_questionary.select.return_value = mock_select

        mock_shell_select = mock.Mock()
        mock_shell_select.ask.return_value = "/bin/bash"

        with mock.patch("docker_tool.wizard.console"):
            with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
                call_count = 0

                def side_effect(*args, **kwargs):
                    nonlocal call_count
                    if "Choose an action" in args[0]:
                        call_count += 1
                        if call_count == 1:
                            return mock_select
                        else:
                            mock_back = mock.Mock()
                            mock_back.ask.return_value = "back"
                            return mock_back
                    elif "Select shell type" in args[0]:
                        return mock_shell_select
                    return mock_select

                mock_questionary.select.side_effect = side_effect
                wizard.manage_container(mock_container)

                mock_docker_client._spawn_shell_in_container.assert_called_once_with(
                    mock_container, "/bin/bash"
                )

    @mock.patch("docker_tool.wizard.questionary")
    def test_execute_action_exec(
        self, mock_questionary, wizard, mock_container, mock_docker_client
    ):
        """Test execute action with exec command"""
        wizard.docker = mock_docker_client

        mock_text = mock.Mock()
        mock_text.ask.return_value = "ls -la"
        mock_questionary.text.return_value = mock_text

        with mock.patch("docker_tool.wizard.console"):
            with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
                wizard.execute_action(mock_container, "exec")

                mock_docker_client._exec_cmd_in_container.assert_called_once_with(
                    mock_container, "ls -la"
                )

    @mock.patch("docker_tool.wizard.questionary")
    def test_execute_action_logs(
        self, mock_questionary, wizard, mock_container, mock_docker_client
    ):
        """Test execute action with logs command"""
        wizard.docker = mock_docker_client

        mock_confirm = mock.Mock()
        mock_confirm.ask.return_value = True
        mock_questionary.confirm.return_value = mock_confirm

        with mock.patch("docker_tool.wizard.console"):
            with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
                wizard.execute_action(mock_container, "logs")

                mock_docker_client._fetch_logs_from_container.assert_called_once_with(
                    mock_container, follow=True
                )

    def test_execute_action_start(self, wizard, mock_container, mock_docker_client):
        """Test execute action with start command"""
        wizard.docker = mock_docker_client

        with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
            wizard.execute_action(mock_container, "start")

            mock_docker_client.start_container.assert_called_once_with(mock_container.id)

    def test_execute_action_stop(self, wizard, mock_container, mock_docker_client):
        """Test execute action with stop command"""
        wizard.docker = mock_docker_client

        with mock.patch("docker_tool.wizard.questionary") as mock_questionary:
            mock_confirm = mock.Mock()
            mock_confirm.ask.return_value = True
            mock_questionary.confirm.return_value = mock_confirm

            with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
                wizard.execute_action(mock_container, "stop")

                mock_docker_client.stop_container.assert_called_once_with(mock_container.id)

    def test_execute_action_restart(self, wizard, mock_container, mock_docker_client):
        """Test execute action with restart command"""
        wizard.docker = mock_docker_client

        with mock.patch("builtins.input"):  # Mock input for "Press Enter to continue"
            wizard.execute_action(mock_container, "restart")

            mock_docker_client.restart_container.assert_called_once_with(mock_container.id)
