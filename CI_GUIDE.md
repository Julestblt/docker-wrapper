# CI/CD and Testing Guide - Docker Tool

## 🎯 Overview

This project uses **only** Python standard tools for testing and CI/CD. No custom bash scripts.

## 🛠 Setup and Commands

### Quick Installation
```bash
# Basic installation
pip install -e .

# Installation with development dependencies
pip install -e ".[dev]"

# Installation with test dependencies only
pip install -e ".[test]"
```

### Tests

#### Unit tests (no external dependencies)
```bash
# Direct Python command
python -m unittest discover tests -p "test_unittest.py" -v

# With Makefile
make test-unit

# For CI
make test-ci
```

#### Complete tests with pytest
```bash
# Direct Python command
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=docker_tool --cov-report=term-missing

# With Makefile
make test
make test-coverage
```

### Code Quality

#### Linting
```bash
# Flake8
python -m flake8 docker_tool tests --max-line-length=100

# With Makefile
make lint
```

#### Formatting
```bash
# Black
python -m black docker_tool tests --line-length=100

# With Makefile
make format
```

#### Type Checking
```bash
# MyPy
python -m mypy docker_tool --ignore-missing-imports

# With Makefile
make type-check
```

### Build and Publish

#### Package Build
```bash
# Direct Python
python -m build

# With Makefile
make build
```

#### Publishing
```bash
# TestPyPI
python -m twine upload --repository testpypi dist/*

# PyPI
python -m twine upload dist/*

# With Makefile
make publish-test
make publish
```

## 🚀 CI/CD with GitHub Actions

The `.github/workflows/ci.yml` file is configured for:

### Job `test`
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Unittest tests (no dependencies)
- Pytest tests with coverage
- Upload to Codecov

### Job `lint`
- Flake8 checking
- Black formatting check
- MyPy type checking

### Job `build`
- Package build
- Twine validation
- Triggered only on push to `main`

## 🧪 Testing with Tox (optional)

To test on multiple Python versions locally:

```bash
# Install tox
pip install tox

# Test on all versions
tox

# Specific tests
tox -e py311          # Python 3.11 only
tox -e lint           # Lint only
tox -e coverage       # Coverage only
tox -e unit-only      # Unit tests only
```

## 📋 Commands for Different Environments

### Local Development
```bash
make dev-install    # Complete installation
make check          # Lint + types + unit tests
make test-coverage  # Tests with coverage
```

### CI/CD
```bash
# Minimal installation
pip install -e .

# Quick tests (CI)
python -m unittest discover tests -p "test_unittest.py" -v

# Complete tests (if dependencies available)
pip install -e ".[test]"
python -m pytest tests/ --cov=docker_tool --cov-report=xml
```

### Production
```bash
# End user installation
pip install docker-tool

# Or from source
pip install -e .
```

## 🔧 Tool Configuration

### pyproject.toml
- Main project configuration
- Optional dependencies (`[dev]`, `[test]`)
- Pytest and coverage configuration

### setup.cfg
- Tool configuration (flake8, mypy, coverage)
- Fallback for tools not supporting pyproject.toml

### tox.ini
- Multi-version Python testing
- Separate environments for different test types

## 💡 Best Practices

1. **Lightweight CI tests**: Use `test-ci` for quick tests
2. **Complete local tests**: Use `test-coverage`
3. **Pre-commit validation**: `make check`
4. **Clean build**: `make clean build`

## 🎭 Advantages of This Approach

- ✅ **Python Standards**: Uses native Python tools
- ✅ **No bash scripts**: More portable and maintainable
- ✅ **Fast CI**: Unittest tests without external dependencies
- ✅ **Flexible**: Makefile for common commands
- ✅ **Multi-Python**: Tests on multiple versions
- ✅ **Quality**: Automatic lint, format, types
