#!/bin/bash
# Script to temporarily disable pre-commit hooks
# Usage: ./scripts/bypass_hooks.sh "commit message"

if [ -z "$1" ]; then
    echo "Usage: $0 'commit message'"
    echo "This will commit with --no-verify to bypass pre-commit hooks"
    echo "Use with caution!"
    exit 1
fi

echo "⚠️ Warning: Bypassing pre-commit hooks!"
echo "Commit message: $1"
echo ""

read -p "Are you sure you want to bypass the hooks? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit --no-verify -m "$1"
    echo "✅ Commit created with hooks bypassed"
else
    echo "❌ Commit cancelled"
fi
