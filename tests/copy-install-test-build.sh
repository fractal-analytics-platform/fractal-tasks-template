#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create empty folder (fail if it already exists)
FOLDER="/tmp/new-project-folder"

# Generate a new project based on the HEAD git reference
echo "Now generate a new project copy in $FOLDER"
copier copy . "$FOLDER" --data-file tests/answers.yml --vcs-ref=HEAD

# Move to the new folder
cd "$FOLDER"

# Install the new project
python3 -m pip install -e .[dev]

# Generate the manifest
python3 src/my_project/dev/create_manifest.py

# Run tests
python3 -m pytest tests

# Build package
python3 -m build
