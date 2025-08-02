# Unit Testing Guide for Docker Tool

## 🎯 Overview

This guide explains how to configure and run tests for your Docker Tool.

## 📁 Test Structure

```
tests/
├── __init__.py
├── test_docker_client.py    # Tests for DockerClient
├── test_cli.py             # Tests for CLI commands
├── test_wizard.py          # Tests for wizard interface
└── test_unittest.py        # Tests using unittest (no dependencies)
```

## 🛠 Installing Test Dependencies

### Option 1: With pytest (recommended)
```bash
pip install pytest pytest-cov pytest-mock
```

### Option 2: No dependencies (unittest only)
```bash
# No additional installation needed
# Uses Python's built-in unittest module
```

## 🚀 Running Tests

### Quick tests with unittest (no dependencies)
```bash
python -m unittest discover tests -p "test_unittest.py" -v
```

### Complete tests with pytest
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=docker_tool --cov-report=term-missing

# Run specific test file
pytest tests/test_docker_client.py -v

# Run specific test method
pytest tests/test_docker_client.py::TestDockerClient::test_find_container_exact_match -v
```

### Using Makefile
```bash
# Unit tests only (no dependencies)
make test-unit

# All tests with pytest
make test

# Tests with coverage
make test-coverage

# CI tests
make test-ci
```

## 📊 Test Coverage

### Generating Coverage Reports
```bash
# Terminal report
pytest tests/ --cov=docker_tool --cov-report=term-missing

# HTML report
pytest tests/ --cov=docker_tool --cov-report=html:htmlcov

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Current Coverage
- `docker_client.py`: ~95% coverage
- `cli.py`: ~90% coverage
- `wizard.py`: ~85% coverage
- Overall: ~90% coverage

## 🔬 Test Details

### DockerClient Tests (`test_docker_client.py`)
Tests for the core Docker operations:
- ✅ Container finding (exact match, regex, multiple matches)
- ✅ Shell spawning
- ✅ Command execution
- ✅ Log fetching
- ✅ Error handling
- ✅ Interactive container selection

### CLI Tests (`test_cli.py`)
Tests for command-line interface:
- ✅ `ps` command
- ✅ `shell` command with pattern matching
- ✅ `exec` command
- ✅ `logs` command
- ✅ `wizard` command

### Wizard Tests (`test_wizard.py`)
Tests for interactive wizard:
- ✅ Container selection
- ✅ Action selection (shell, exec, logs)
- ✅ Exit handling
- ✅ Navigation (back/forth)

### Unittest Tests (`test_unittest.py`)
Same functionality as above but using only Python's built-in unittest module:
- ✅ No external dependencies
- ✅ Suitable for CI environments
- ✅ All core functionality covered

## 🎭 Mocking Strategy

### Docker API Mocking
```python
@mock.patch('docker_tool.docker_client.docker.from_env')
def test_function(self, mock_docker_from_env):
    mock_client = mock.Mock()
    mock_docker_from_env.return_value = mock_client
    # Test implementation
```

### Container Mocking
```python
def setUp(self):
    self.mock_container = mock.Mock()
    self.mock_container.id = "test123456789"
    self.mock_container.short_id = "test123"
    self.mock_container.name = "test-container"
    self.mock_container.status = "running"
```

### CLI Testing with Typer
```python
def test_cli_command(self):
    runner = CliRunner()
    result = runner.invoke(app, ["command", "args"])
    assert result.exit_code == 0
```

## 🐛 Debugging Tests

### Running with Debug Output
```bash
# Verbose output
pytest tests/ -v -s

# Show print statements
pytest tests/ --capture=no

# Drop into debugger on failure
pytest tests/ --pdb
```

### Debugging Specific Issues
```bash
# Test only failed tests from last run
pytest tests/ --lf

# Stop on first failure
pytest tests/ -x

# Run tests in parallel (if you have pytest-xdist)
pytest tests/ -n auto
```

## 🎯 Testing Best Practices

### 1. Mock External Dependencies
- Always mock Docker API calls
- Mock file system operations
- Mock user input (questionary)

### 2. Test Error Scenarios
- Container not found
- Docker daemon not running
- Network errors
- Invalid input

### 3. Test Edge Cases
- Empty container lists
- Multiple matches
- Special characters in names
- Long output streams

### 4. Keep Tests Independent
- Each test should be able to run alone
- Use `setUp()` and `tearDown()` properly
- Don't rely on test execution order

## 🔧 CI/CD Integration

### GitHub Actions
The project includes automated testing on:
- Python 3.9, 3.10, 3.11, 3.12
- Ubuntu, Windows, macOS (if configured)

### Test Commands for CI
```bash
# Fast tests (no dependencies)
python -m unittest discover tests -p "test_unittest.py" -v

# Complete tests (with dependencies)
pip install pytest pytest-cov
pytest tests/ --cov=docker_tool --cov-report=xml
```

## 📈 Adding New Tests

### For New Features
1. Create test methods in appropriate test file
2. Follow naming convention: `test_feature_scenario`
3. Include both success and failure cases
4. Add mocking for external dependencies

### Example Test Structure
```python
def test_new_feature_success(self):
    """Test new feature with valid input"""
    # Arrange
    # Act
    # Assert

def test_new_feature_failure(self):
    """Test new feature with invalid input"""
    # Arrange
    # Act
    # Assert
```

## 🏆 Test Quality Metrics

### Current Status
- ✅ 13 unittest tests passing
- ✅ ~15 pytest tests passing
- ✅ ~90% code coverage
- ✅ All core functionality tested
- ✅ Error scenarios covered
- ✅ CI integration working

### Goals
- Maintain >85% coverage
- Test all new features
- Keep test execution fast (<30s)
- Ensure tests work without Docker installed
