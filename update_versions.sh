#!/bin/bash

NEW_VERSION="3.12.2"
TESTIT_API_CLIENT_VERSION="7.5.0"

echo "Updating all adapters to version: $NEW_VERSION"
echo "Updating testit-api-client to version: $TESTIT_API_CLIENT_VERSION"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Project root: $PROJECT_ROOT"

# Update VERSION in all setup.py files
for setup_file in "$PROJECT_ROOT"/testit-*/setup.py; do
    adapter_name=$(basename "$(dirname "$setup_file")")
    echo "Updating $adapter_name to version $NEW_VERSION"
    sed -i "s/^VERSION = \".*\"/VERSION = \"$NEW_VERSION\"/" "$setup_file"
done

# Special handling for python-commons to update testit-api-client version
PYTHON_COMMONS_SETUP="$PROJECT_ROOT/testit-python-commons/setup.py"
echo "Updating testit-api-client version in python-commons"
sed -i "s/testit-api-client==.*/testit-api-client==$TESTIT_API_CLIENT_VERSION']/" "$PYTHON_COMMONS_SETUP"

echo "Version update completed!"
