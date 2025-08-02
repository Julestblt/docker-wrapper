# Docker Tool

<div align="center">

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)

**Smart Docker container management with an elegant CLI**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Features

### Core Features
- **Interactive Wizard Mode**: Beautiful TUI for container management
- **Smart Container Search**: Find containers by ID, name, or partial match
- **Rich Output**: Colorful tables and formatted output with rich
- **Intelligent Commands**: Short commands that do what you expect
- **Docker API Integration**: Direct Docker SDK usage for better performance
- **Smart Error Handling**: User-friendly error messages and suggestions

### Advanced Features
- **Container Status Indicators**: Visual status in wizard mode
- **Auto-Detection**: Automatically detects Docker/Docker Compose
- **Shell Completion**: Tab completion for commands (bash, zsh, fish)
- **Regex Filtering**: Advanced container filtering with regex support

## Installation

### Prerequisites

- Python 3.8+
- Docker installed and running
- pip package manager

### Install from PyPI

```bash
pip install docker-tool
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/julestblt/docker-wrapper.git
cd docker-wrapper

# Install in development mode
pip install -e .
```

### Enable Shell Completion

```bash
# Bash
dtool --install-completion bash

# Zsh
dtool --install-completion zsh

# Fish
dtool --install-completion fish
```

## Quick Start

### Interactive Wizard Mode

The easiest way to manage containers:

```bash
# Launch the interactive wizard
dtool wizard
```

Features:
- Visual container selection with status indicators
- Context-aware actions based on container state
- Beautiful prompts with questionary
- Navigate with arrow keys, select with Enter

### List Containers

```bash
# List running containers
dtool ps

# List all containers (including stopped)
dtool ps -a

# Interactive mode - select and manage containers
dtool ps -i

# Filter containers by name/ID
dtool ps nginx
dtool ps e5d

# Use regex filtering
dtool ps "^web-.*" -r
```

## Documentation

### Container Management Commands

#### Shell Access

```bash
# Quick shell access (auto-detects bash/sh)
dtool shell nginx
dtool shell backend
dtool shell e5d  # Partial ID works!

# Use specific shell
dtool shell alpine /bin/sh
dtool shell ubuntu /bin/zsh
```

#### Execute Commands

```bash
# Run single commands
dtool exec nginx "ls -la"
dtool exec backend cat /etc/hosts
dtool exec web "ps aux | grep node"
```

#### View Logs

```bash
# View last 100 lines (default)
dtool logs nginx

# Follow logs in real-time
dtool logs backend -f
dtool logs backend --follow

# View specific number of lines
dtool logs app --tail 50
```

#### Container Lifecycle

```bash
# Start containers
dtool start nginx
dtool start backend frontend db  # Multiple containers

# Stop containers
dtool stop nginx
dtool stop backend --force  # Force stop

# Restart containers
dtool restart nginx
dtool restart backend --force

# Remove containers
dtool rm old-container
dtool rm test-app --force  # Force remove running container
```

### Smart Container Search

The tool intelligently searches for containers in this order:

1. **Exact ID match**: Full container ID
2. **ID prefix**: Beginning of container ID
3. **Exact name**: Full container name
4. **Partial match**: Grep-like search in names

```bash
# Examples
dtool shell e5d4a2b1          # ID prefix
dtool shell nginx              # Exact name
dtool shell backend            # Matches: my-backend, backend-api, etc.
dtool logs "web|api" -r        # Regex: matches web OR api
```

### Advanced Usage

#### Filter and Manage

```bash
# List only Redis containers
dtool ps redis

# Stop all containers matching pattern
dtool ps "test-" -r | xargs -I {} dtool stop {}

# View logs of all API containers
dtool ps "api" | xargs -I {} dtool logs {} --tail 20
```

#### Error Handling Examples

The tool provides helpful error messages:

```bash
$ dtool shell nonexistent
╭─ Container Error ─╮
│ Container not found! │
│                      │
│ No container with    │
│ name or ID           │
│ 'nonexistent' was    │
│ found.               │
│                      │
│ Try running:         │
│ • dtool ps -a        │
│ • dtool ps           │
╰──────────────────────╯
```

## Project Structure

```
docker-tool/
├── docker_tool/
│   ├── __init__.py
│   ├── cli.py           # Main CLI entry point
│   ├── docker_client.py # Docker SDK wrapper
│   ├── wizard.py        # Interactive wizard mode
│   ├── utils.py         # Utility functions
│   └── version.py       # Version information
├── requirements.txt     # Python dependencies
├── setup.py            # Package configuration
└── README.md           # This file
```

## Why Docker Tool?

| Feature | Docker CLI | Docker Tool |
|---------|------------|-------------|
| Open shell | `docker exec -it nginx /bin/bash` | `dtool shell nginx` |
| View logs | `docker logs -f --tail 100 nginx` | `dtool logs nginx -f` |
| Stop container | `docker stop nginx` | `dtool stop nginx` |
| Interactive mode | Not available | `dtool wizard` |
| Smart search | Exact ID/name required | Partial match, regex |
| Error messages | Technical errors | User-friendly guidance |

## Development

### Setup Development Environment

```bash
# Clone the repo
git clone https://github.com/yourusername/docker-tool.git
cd docker-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

This project uses automated code quality tools:

- **Pre-commit hooks**: Automatically run on every commit
- **Black**: Code formatting (line length: 88 characters)
- **Flake8**: PEP8 compliance and code quality
- **Pytest**: Automated testing before commits

#### Development Setup

```bash
# Install with development dependencies and hooks
make dev-install

# Manual pre-commit hooks setup (if needed)
pre-commit install

# Run all quality checks
make check

# Run pre-commit hooks manually
make hooks
```

#### Code Standards

- Follow PEP 8 (enforced by flake8)
- Use type hints where possible
- Add docstrings to public functions
- Maintain test coverage above 50%
- All commits must pass pre-commit hooks

See [HOOKS.md](HOOKS.md) for detailed information about pre-commit hooks.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) - The amazing CLI framework
- Styled with [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- Interactive mode powered by [Questionary](https://github.com/tmbo/questionary)
- Docker SDK for Python

---

<div align="center">
Made with love by developers who hate long Docker commands
</div>
