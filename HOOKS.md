# Pre-commit Hooks Guide

## Installation

Pre-commit hooks are already installed in this project. They automatically run on every `git commit`.

## What the hooks do

1. **trailing-whitespace**: Removes trailing whitespace at the end of lines
2. **end-of-file-fixer**: Ensures there's a blank line at the end of files
3. **check-yaml**: Validates YAML file syntax
4. **check-added-large-files**: Prevents adding large files to the repository
5. **check-merge-conflict**: Detects merge conflict markers
6. **black**: Automatically formats Python code
7. **flake8**: Checks code compliance with PEP8 standards
8. **pytest**: Runs tests before each commit

## If a commit fails

If your commit fails due to hooks:

1. **Formatting errors**: `black` fixes automatically, run `git add` then `git commit` again
2. **flake8 errors**: Fix the code errors then commit again
3. **Failing tests**: Fix the tests then commit again

## Useful commands

```bash
# Run all hooks manually
pre-commit run --all-files

# Run a specific hook
pre-commit run black
pre-commit run flake8
pre-commit run pytest

# Update hooks to latest versions
pre-commit autoupdate

# Bypass hooks (use with caution)
git commit --no-verify -m "message"
# or
./scripts/bypass_hooks.sh "message"

# Using Makefile shortcuts
make hooks              # Run all hooks
make hooks-update       # Update hooks
make format            # Run black formatting
make lint              # Run flake8 linting
make test              # Run tests
```

## Configuration

Hooks are configured in `.pre-commit-config.yaml`.
Flake8 settings are in `setup.cfg`.

## Uninstall (if needed)

```bash
pre-commit uninstall
```
