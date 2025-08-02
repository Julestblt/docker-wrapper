# Docker Tool - Developer Guide

## 🔧 Quick Setup

```bash
# 1. Clone the project
git clone https://github.com/Julestblt/docker-wrapper.git
cd docker-wrapper

# 2. Development installation
make dev-install

# 3. Verification
make check
```

## 🧪 Testing

```bash
# Quick tests (for CI)
make test-ci

# Unit tests only
make test-unit

# Complete tests with coverage
make test-coverage

# All checks
make check
```

## 🚀 Development Workflow

### 1. Before committing
```bash
make check           # Lint + types + tests
make format          # Format code
```

### 2. Continuous testing
```bash
# Terminal 1: development
# Terminal 2: automatic tests
make test-unit       # Repeat after each modification
```

### 3. Before pushing
```bash
make clean           # Clean up
make test-coverage   # Complete tests
make build           # Verify build
```

## 📦 Publishing

```bash
# Test version
make publish-test

# Production version
make publish
```

## 🛠 Useful Commands

```bash
make help           # Show all commands
make clean          # Clean temporary files
make lint           # Code checking
make format         # Automatic formatting
make type-check     # Type checking
```
