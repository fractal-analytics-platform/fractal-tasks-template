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

# Initialize git (needed for versioning)
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git init
git add .
git commit -m "Initial commit"
git tag -a "0.1.0" -m "First release"

# Install the new project
python3 -m pip install -e .[dev]

# Generate the manifest
fractal-manifest create --package my_project

# Run tests
python3 -m pytest tests

# Build package
hatch build
