# Docker Tool

🐳 Smart Docker container management with an elegant CLI.

## Features

- **Smart Container Search**: Find containers by ID, name, or partial match
- **Rich Output**: Colorful tables and formatted output with rich
- **Intelligent Commands**: Short commands that do what you expect
- **Docker Compose Support**: Automatically detects and uses docker-compose

## Installation

### Prerequisites

- Python 3.8+
- Docker installed and running

### Install

```bash
git clone <your-repo>
cd docker-tool

pip install -r requirements.txt

chmod +x docker_tool.py

sudo ln -s $(pwd)/docker_tool.py /usr/local/bin/dtool
```

## Usage

### Quick Commands

#### List Containers

```bash
# List running containers
dtool ps

# List all containers
dtool ps -a

# Interactive container selection
dtool ps -i
```

#### Container Management

```bash
# Open shell (intelligent container search)
dtool shell nginx
dtool shell backend
dtool shell e5d  # Partial ID

# Execute commands
dtool exec nginx ls -la
dtool exec backend cat /etc/hosts

# View logs
dtool logs nginx
dtool logs backend -f

# Container lifecycle
dtool stop nginx
dtool start nginx
dtool restart backend
dtool rm nginx
dtool rm backend -f
```

### Smart Container Search

The tool intelligently searches for containers:

1. **By ID**: Matches container ID prefix
   ```bash
   dtool shell e5d4a2  # Matches container starting with e5d4a2
   ```

2. **By exact name**: Matches full container name
   ```bash
   dtool shell my-nginx  # Matches container named "my-nginx"
   ```

3. **By partial name**: Grep-like search
   ```bash
   dtool shell backend  # Matches "app-backend", "backend-api", etc.
   ```

4. **Interactive selection**: When multiple matches found
   ```bash
   dtool shell app  # Shows menu if multiple containers contain "app"
   ```

## Examples

### Common Workflows

```bash
# Quick shell access
dtool shell backend

# Check logs of multiple services
dtool logs frontend
dtool logs backend

# Restart a service
dtool restart nginx
```

### Advanced Usage

```bash
# Use specific shell
dtool shell alpine --shell /bin/sh

# Force stop container
dtool stop stubborn-container --force

# Follow logs
dtool logs app -f
```

## Project Structure

```bash
docker-wrapper/
├── requirements.txt     # Python dependencies
└── docker_tool/
    ├── __init__.py
    ├── cli.py           # Main CLI entry point
    ├── docker_client.py # Docker command wrapper
    ├── version.py       # Version information
    └── utils.py         # Utility functions
```

## Why Docker Tool?

- **Shorter Commands**: `dtool shell nginx` vs `docker exec -it nginx /bin/bash`
- **Smart Search**: No need to remember full container IDs or names
- **Beautiful Output**: Rich formatting makes information easy to read
- **Interactive Mode**: Perfect for when you're not sure what you want to do
- **Error Handling**: Graceful fallbacks (e.g., sh when bash unavailable)

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use in your projects!