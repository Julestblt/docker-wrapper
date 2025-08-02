import pytest
import unittest.mock as mock
from docker.errors import NotFound, APIError
from docker_tool.docker_client import DockerClient


class TestDockerClient:
    """Tests for the DockerClient class"""

    @pytest.fixture
    def client(self):
        """Create a DockerClient instance for testing"""
        return DockerClient(capture=True)

    @pytest.fixture
    def mock_docker_from_env(self):
        """Mock docker.from_env() to avoid real Docker calls"""
        with mock.patch("docker_tool.docker_client.docker.from_env") as mock_docker:
            yield mock_docker

    @pytest.fixture
    def mock_container(self):
        """Create a mock container object"""
        container = mock.Mock()
        container.id = "test123456789"
        container.short_id = "test123456"
        container.name = "test-container"
        container.status = "running"
        container.image.tags = ["nginx:latest"]
        container.ports = {}
        return container

    def test_is_daemon_running_success(self, client, mock_docker_from_env):
        """Test Docker daemon is running"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        result = client.is_daemon_running()

        assert result is True
        mock_client.ping.assert_called_once()

    def test_is_daemon_running_failure(self, client, mock_docker_from_env):
        """Test Docker daemon is not running"""
        from docker.errors import DockerException

        mock_docker_from_env.side_effect = DockerException("Docker not available")

        result = client.is_daemon_running()

        assert result is False

    def test_find_container_exact_match_by_id(
        self, client, mock_docker_from_env, mock_container
    ):
        """Test finding container by exact ID match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        container, matches = client.find_container("test123456")

        assert container == mock_container
        assert matches == []

    def test_find_container_exact_match_by_name(
        self, client, mock_docker_from_env, mock_container
    ):
        """Test finding container by exact name match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        container, matches = client.find_container("test-container")

        assert container == mock_container
        assert matches == []

    def test_find_container_regex_match_single(
        self, client, mock_docker_from_env, mock_container
    ):
        """Test finding container by regex pattern with single match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        container, matches = client.find_container("test.*")

        assert container == mock_container
        assert matches == []

    def test_find_container_regex_match_multiple(self, client, mock_docker_from_env):
        """Test finding container by regex pattern with multiple matches"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client

        container1 = mock.Mock()
        container1.id = "test123"
        container1.name = "test-web"
        container2 = mock.Mock()
        container2.id = "test456"
        container2.name = "test-api"

        mock_client.containers.list.return_value = [container1, container2]

        container, matches = client.find_container("test.*")

        assert container is None
        assert len(matches) == 2
        assert container1 in matches
        assert container2 in matches

    def test_find_container_no_match(self, client, mock_docker_from_env):
        """Test finding container with no matches"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = []

        container, matches = client.find_container("nonexistent")

        assert container is None
        assert matches == []

    def test_spawn_shell_container_not_running(
        self, client, mock_docker_from_env, mock_container
    ):
        """Test spawn shell when container is not running"""
        mock_container.status = "stopped"
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        with mock.patch("docker_tool.docker_client.console") as mock_console:
            client.spawn_shell("test-container")
            mock_console.print.assert_called()

    @mock.patch("docker_tool.docker_client.os.execvp")
    def test_spawn_shell_success(
        self, mock_execvp, client, mock_docker_from_env, mock_container
    ):
        """Test successful spawn shell"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        with mock.patch("docker_tool.docker_client.console"):
            client.spawn_shell("test-container", "/bin/bash")

        mock_execvp.assert_called_once_with(
            "docker", ["docker", "exec", "-it", "test123456789", "/bin/bash"]
        )

    def test_exec_cmd_container_not_running(
        self, client, mock_docker_from_env, mock_container
    ):
        """Test exec command when container is not running"""
        mock_container.status = "stopped"
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        with mock.patch("docker_tool.docker_client.console") as mock_console:
            client.exec_cmd("test-container", "ls -la")
            mock_console.print.assert_called()

    def test_exec_cmd_success(self, client, mock_docker_from_env, mock_container):
        """Test successful exec command"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        mock_exec_instance = {"Id": "exec123"}
        mock_client.api.exec_create.return_value = mock_exec_instance
        mock_client.api.exec_start.return_value = [
            b"output line 1\n",
            b"output line 2\n",
        ]

        with mock.patch("docker_tool.docker_client.console"):
            with mock.patch("builtins.print") as mock_print:
                client.exec_cmd("test-container", "ls -la")

        mock_client.api.exec_create.assert_called_once_with(
            "test123456789", ["ls", "-la"], tty=True, stdin=True
        )
        mock_client.api.exec_start.assert_called_once_with("exec123", stream=True)
        # Vérifier qu'au moins un appel à print a été fait
        assert mock_print.call_count >= 1

    def test_fetch_logs_success(self, client, mock_docker_from_env, mock_container):
        """Test successful log fetching"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [mock_container]

        mock_container.logs.return_value = b"Log line 1\nLog line 2\n"

        with mock.patch("docker_tool.docker_client.console"):
            with mock.patch("builtins.print") as mock_print:
                client.fetch_logs("test-container", follow=False)

        mock_container.logs.assert_called_once()
        mock_print.assert_called_once_with("Log line 1\nLog line 2\n", end="")

    def test_handle_docker_error_not_found(self, client):
        """Test error handling for NotFound exception"""
        error = NotFound("Container not found")

        with mock.patch("docker_tool.docker_client.console") as mock_console:
            client._handle_docker_error(error, "test-container")
            mock_console.print.assert_called_once()

    def test_handle_docker_error_api_error(self, client):
        """Test error handling for APIError exception"""
        error = APIError("API Error occurred")

        with mock.patch("docker_tool.docker_client.console") as mock_console:
            client._handle_docker_error(error)
            mock_console.print.assert_called_once()

    def test_list_containers_with_filter(self, client, mock_docker_from_env):
        """Test listing containers with filter"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client

        container1 = mock.Mock()
        container1.name = "web-server"
        container1.id = "abc123"
        container2 = mock.Mock()
        container2.name = "database"
        container2.id = "def456"

        mock_client.containers.list.return_value = [container1, container2]

        result = client.list_containers(all=True, filter="web", regex=True)

        assert len(result) == 1
        assert result[0].name == "web-server"

    def test_list_containers_exact_filter(self, client, mock_docker_from_env):
        """Test listing containers with exact filter"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client

        container1 = mock.Mock()
        container1.name = "web"
        container1.id = "abc123"
        container2 = mock.Mock()
        container2.name = "web-server"
        container2.id = "def456"

        mock_client.containers.list.return_value = [container1, container2]

        result = client.list_containers(all=True, filter="web", regex=False)

        assert len(result) == 1
        assert result[0].name == "web"
