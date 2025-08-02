import pytest
import unittest.mock as mock
from typer.testing import CliRunner
from docker_tool.cli import app
from docker_tool.docker_client import DockerClient


class TestCLI:
    """Tests for the CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create a CliRunner for testing Typer commands"""
        return CliRunner()
    
    @pytest.fixture
    def mock_docker_client(self):
        """Mock the DockerClient to avoid real Docker calls"""
        with mock.patch('docker_tool.cli.docker') as mock_client:
            mock_client.is_daemon_running.return_value = True
            yield mock_client
    
    def test_version_command(self, runner):
        """Test the version command"""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Docker Tool" in result.stdout
    
    def test_help_command(self, runner):
        """Test the help command"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Docker operations made simple" in result.stdout
    
    def test_ps_command_success(self, runner, mock_docker_client):
        """Test the ps command with successful execution"""
        mock_container = mock.Mock()
        mock_container.short_id = "abc123"
        mock_container.name = "test-container"
        mock_container.image.tags = ["nginx:latest"]
        mock_container.status = "running"
        mock_container.ports = {}
        
        mock_docker_client.list_containers.return_value = [mock_container]
        mock_docker_client.print_containers_rich = mock.Mock()
        
        result = runner.invoke(app, ["ps"])
        
        assert result.exit_code == 0
        mock_docker_client.list_containers.assert_called_once()
        mock_docker_client.print_containers_rich.assert_called_once()
    
    def test_ps_command_with_filter(self, runner, mock_docker_client):
        """Test the ps command with container filter"""
        mock_docker_client.list_containers.return_value = []
        mock_docker_client.print_containers_rich = mock.Mock()
        
        result = runner.invoke(app, ["ps", "nginx"])
        
        assert result.exit_code == 0
        mock_docker_client.list_containers.assert_called_with(
            all=False, filter="nginx", regex=False
        )
    
    def test_shell_command(self, runner, mock_docker_client):
        """Test the shell command"""
        mock_docker_client.spawn_shell = mock.Mock()
        
        result = runner.invoke(app, ["shell", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.spawn_shell.assert_called_once_with(
            container_pattern="test-container", shell="/bin/sh"
        )
    
    def test_shell_command_with_custom_shell(self, runner, mock_docker_client):
        """Test the shell command with custom shell"""
        mock_docker_client.spawn_shell = mock.Mock()
        
        result = runner.invoke(app, ["shell", "test-container", "/bin/bash"])
        
        assert result.exit_code == 0
        mock_docker_client.spawn_shell.assert_called_once_with(
            container_pattern="test-container", shell="/bin/bash"
        )
    
    def test_exec_command(self, runner, mock_docker_client):
        """Test the exec command"""
        mock_docker_client.exec_cmd = mock.Mock()
        
        result = runner.invoke(app, ["exec", "test-container", "ls -la"])
        
        assert result.exit_code == 0
        mock_docker_client.exec_cmd.assert_called_once_with(
            container_pattern="test-container", command="ls -la"
        )
    
    def test_logs_command(self, runner, mock_docker_client):
        """Test the logs command"""
        mock_docker_client.fetch_logs = mock.Mock()
        
        result = runner.invoke(app, ["logs", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.fetch_logs.assert_called_once_with(
            container_pattern="test-container", follow=False
        )
    
    def test_logs_command_with_follow(self, runner, mock_docker_client):
        """Test the logs command with follow option"""
        mock_docker_client.fetch_logs = mock.Mock()
        
        result = runner.invoke(app, ["logs", "test-container", "--follow"])
        
        assert result.exit_code == 0
        mock_docker_client.fetch_logs.assert_called_once_with(
            container_pattern="test-container", follow=True
        )
    
    def test_docker_daemon_not_running(self, runner):
        """Test behavior when Docker daemon is not running"""
        with mock.patch('docker_tool.cli.docker') as mock_client:
            mock_client.is_daemon_running.return_value = False
            
            result = runner.invoke(app, ["ps"])
            
            assert result.exit_code == 1
            assert "Docker daemon is not running" in result.stdout
    
    def test_start_command(self, runner, mock_docker_client):
        """Test the start command"""
        mock_docker_client.start_container = mock.Mock()
        
        result = runner.invoke(app, ["start", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.start_container.assert_called_once_with(container_id="test-container")
    
    def test_stop_command(self, runner, mock_docker_client):
        """Test the stop command"""
        mock_docker_client.stop_container = mock.Mock()
        
        result = runner.invoke(app, ["stop", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.stop_container.assert_called_once_with(container_id="test-container", force=False)
    
    def test_restart_command(self, runner, mock_docker_client):
        """Test the restart command"""
        mock_docker_client.restart_container = mock.Mock()
        
        result = runner.invoke(app, ["restart", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.restart_container.assert_called_once_with(container_id="test-container", force=False)
    
    def test_remove_command(self, runner, mock_docker_client):
        """Test the remove command"""
        mock_docker_client.remove_container = mock.Mock()
        
        result = runner.invoke(app, ["rm", "test-container"])
        
        assert result.exit_code == 0
        mock_docker_client.remove_container.assert_called_once_with(container_id="test-container", force=False)
