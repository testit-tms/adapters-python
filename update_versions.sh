#!/bin/bash

NEW_VERSION="5.1.4"

echo "Updating all adapters to version: $NEW_VERSION"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=$SCRIPT_DIR

echo "Project root: $PROJECT_ROOT"

# Update VERSION in all setup.py files
for setup_file in "$PROJECT_ROOT"/testit-*/setup.py; do
    adapter_name=$(basename "$(dirname "$setup_file")")
    echo "Updating $adapter_name to version $NEW_VERSION"
    sed -i "s/^VERSION = \".*\"/VERSION = \"$NEW_VERSION\"/" "$setup_file"
done
echo "Version update completed!"
