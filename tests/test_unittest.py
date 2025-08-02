import unittest
import unittest.mock as mock
import sys
import os
from docker.errors import NotFound, APIError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from docker_tool.docker_client import DockerClient  # noqa: E402


class TestDockerClientUnittest(unittest.TestCase):
    """Tests for DockerClient using unittest (no pytest dependency)"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = DockerClient(capture=True)

        self.mock_container = mock.Mock()
        self.mock_container.id = "test123456789"
        self.mock_container.short_id = "test123"
        self.mock_container.name = "test-container"
        self.mock_container.status = "running"
        self.mock_container.image.tags = ["nginx:latest"]
        self.mock_container.ports = {}

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_is_daemon_running_success(self, mock_docker_from_env):
        """Test Docker daemon is running"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.ping.return_value = True

        result = self.client.is_daemon_running()

        self.assertTrue(result)
        mock_client.ping.assert_called_once()

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_is_daemon_running_failure(self, mock_docker_from_env):
        """Test Docker daemon is not running"""
        from docker.errors import DockerException

        mock_docker_from_env.side_effect = DockerException("Docker not available")

        result = self.client.is_daemon_running()

        self.assertFalse(result)

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_find_container_exact_match_by_id(self, mock_docker_from_env):
        """Test finding container by exact ID match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        container, matches = self.client.find_container("test123")

        self.assertEqual(container, self.mock_container)
        self.assertEqual(matches, [])

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_find_container_exact_match_by_name(self, mock_docker_from_env):
        """Test finding container by exact name match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        container, matches = self.client.find_container("test-container")

        self.assertEqual(container, self.mock_container)
        self.assertEqual(matches, [])

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_find_container_regex_match_single(self, mock_docker_from_env):
        """Test finding container by regex pattern with single match"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        container, matches = self.client.find_container("test.*")

        self.assertEqual(container, self.mock_container)
        self.assertEqual(matches, [])

    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_find_container_no_match(self, mock_docker_from_env):
        """Test finding container with no matches"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = []

        container, matches = self.client.find_container("nonexistent")

        self.assertIsNone(container)
        self.assertEqual(matches, [])

    @mock.patch("docker_tool.docker_client.console")
    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_spawn_shell_container_not_running(self, mock_docker_from_env, mock_console):
        """Test spawn shell when container is not running"""
        self.mock_container.status = "stopped"
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        self.client.spawn_shell("test-container")
        mock_console.print.assert_called()

    @mock.patch("docker_tool.docker_client.os.execvp")
    @mock.patch("docker_tool.docker_client.console")
    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_spawn_shell_success(self, mock_docker_from_env, mock_console, mock_execvp):
        """Test successful spawn shell"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        self.client.spawn_shell("test-container", "/bin/bash")

        mock_execvp.assert_called_once_with(
            "docker", ["docker", "exec", "-it", "test123456789", "/bin/bash"]
        )

    @mock.patch("docker_tool.docker_client.console")
    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_exec_cmd_container_not_running(self, mock_docker_from_env, mock_console):
        """Test exec command when container is not running"""
        self.mock_container.status = "stopped"
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        self.client.exec_cmd("test-container", "ls -la")
        mock_console.print.assert_called()

    @mock.patch("builtins.print")
    @mock.patch("docker_tool.docker_client.console")
    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_exec_cmd_success(self, mock_docker_from_env, mock_console, mock_print):
        """Test successful exec command"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        mock_exec_instance = {"Id": "exec123"}
        mock_client.api.exec_create.return_value = mock_exec_instance
        mock_client.api.exec_start.return_value = [
            b"output line 1\n",
            b"output line 2\n",
        ]

        self.client.exec_cmd("test-container", "ls -la")

        mock_client.api.exec_create.assert_called_once_with(
            "test123456789", ["ls", "-la"], tty=True, stdin=True
        )
        mock_client.api.exec_start.assert_called_once_with("exec123", stream=True)
        self.assertGreaterEqual(mock_print.call_count, 1)

    @mock.patch("builtins.print")
    @mock.patch("docker_tool.docker_client.console")
    @mock.patch("docker_tool.docker_client.docker.from_env")
    def test_fetch_logs_success(self, mock_docker_from_env, mock_console, mock_print):
        """Test successful log fetching"""
        mock_client = mock.Mock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = [self.mock_container]

        self.mock_container.logs.return_value = b"Log line 1\nLog line 2\n"

        self.client.fetch_logs("test-container", follow=False)

        self.mock_container.logs.assert_called_once()
        mock_print.assert_called_once_with("Log line 1\nLog line 2\n", end="")

    @mock.patch("docker_tool.docker_client.console")
    def test_handle_docker_error_not_found(self, mock_console):
        """Test error handling for NotFound exception"""
        error = NotFound("Container not found")

        self.client._handle_docker_error(error, "test-container")
        mock_console.print.assert_called_once()

    @mock.patch("docker_tool.docker_client.console")
    def test_handle_docker_error_api_error(self, mock_console):
        """Test error handling for APIError exception"""
        error = APIError("API Error occurred")

        self.client._handle_docker_error(error)
        mock_console.print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
