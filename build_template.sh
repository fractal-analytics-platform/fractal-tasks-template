#!/bin/bash

# This script build a template project from an existing project.
#
# In details:
# 1. It clones the existing project into a SOURCE_DIR.
# 2. It copies the relevant files from SOURCE_DIR to TEMPLATE_DIR.
# 3. It uses 'sed' to replace specific strings in the copied files to make them generic.
# 4. It change the files extensions to jinja2 template files (.jinja).
#

# Constants and variables
# Start of safe zone

# Directory where the template will be built
TEMPLATE_DIR="template"
SOURCE_DIR="."

# Files and directories to be copied from SOURCE_DIR to TEMPLATE_DIR
TO_COPY=(
    "$SOURCE_DIR/src"
    "$SOURCE_DIR/tests"
    "$SOURCE_DIR/pyproject.toml"
    "$SOURCE_DIR/.gitignore"
    "$SOURCE_DIR/.pre-commit-config.yaml"
    "$SOURCE_DIR/.github"
)

TO_BE_REMOVED=(
    "$TEMPLATE_DIR/tests/copier"
    "$TEMPLATE_DIR/.github/workflows/copier_ci.yml"
    "$TEMPLATE_DIR/.github/workflows/github_release.yaml"
    "$TEMPLATE_DIR/.github/workflows/github_release.yml"
)

# File to be templatized (i.e., where keywords will be replaced)
FILES_TO_TEMPLATIZE=(
    "$TEMPLATE_DIR/pyproject.toml"
    "$TEMPLATE_DIR/.github/workflows/build_and_test.yml"
    "$TEMPLATE_DIR/src/fractal_tasks_template/__init__.py"
    "$TEMPLATE_DIR/src/fractal_tasks_template/example_segmentation_task.py"
    "$TEMPLATE_DIR/src/fractal_tasks_template/dev/task_list.py"
    "$TEMPLATE_DIR/src/fractal_tasks_template/dev/docs_info/example_segmentation_task.md"
    "$TEMPLATE_DIR/src/fractal_tasks_template/__FRACTAL_MANIFEST__.json"
    "$TEMPLATE_DIR/tests/__init__.py"
    "$TEMPLATE_DIR/tests/test_task.py"
    "$TEMPLATE_DIR/tests/test_valid_args_schemas.py"
)

# Keywords to be replaced and their jinja2 template equivalents
AUTHOR_NAME=("Fractal Task Author" "{{ author_name }}")
AUTHOR_EMAIL=("task_author@example.com" "{{ author_email }}")
PROJECT_NAME=("fractal-tasks-template" "{{ project_name }}")
PACKAGE_NAME=("fractal_tasks_template" "{{ package_name }}")
PROJECT_URL=("task_author@example.com" "{{ project_url }}")
PROJECT_SHORT_DESCRIPTION=("Collection of example tasks for the Fractal framework" "{{ project_short_description }}")
CI_PYTHON=("{{ matrix.python-version }}" "{{ '{{' }}  matrix.python-version {{ '{{' }} }}")
CI_OS=("{{ matrix.os }}" "{{ '{{' }}  matrix.os {{ '{{' }} }}")

# Task specific
# - Segmentation task
segmentation_script_name="{{ segmentation_task_name | lower | replace('-', '_') | replace(' ', '_') }}_task"
SEGMENTATION_TASK_NAME=("Example Segmentation Task" "{{ segmentation_task_name }}")
SEGMENTATION_TASK_FUNCTION=("example_segmentation_task" "$segmentation_script_name")


KEYWORD_MAP=(
    "${AUTHOR_NAME[@]}"
    "${AUTHOR_EMAIL[@]}"
    "${PROJECT_NAME[@]}"
    "${PACKAGE_NAME[@]}"
    "${PROJECT_URL[@]}"
    "${PROJECT_SHORT_DESCRIPTION[@]}"
    "${segmentation_script_name[@]}"
    "${CI_PYTHON[@]}"
    "${CI_OS[@]}"
    "${SEGMENTATION_TASK_NAME[@]}"
    "${SEGMENTATION_TASK_FUNCTION[@]}"
)

# File to rename (i.e., where keywords will be replaced in the file names)
RENAME_TASK_SCRIPT=(
    "$TEMPLATE_DIR/src/fractal_tasks_template/example_segmentation_task.py.jinja"
    "$TEMPLATE_DIR/src/fractal_tasks_template/$segmentation_script_name.py.jinja"
)

RENAME_DOC=(
    "$TEMPLATE_DIR/src/fractal_tasks_template/dev/docs_info/example_segmentation_task.md.jinja"
    "$TEMPLATE_DIR/src/fractal_tasks_template/dev/docs_info/$segmentation_script_name.md.jinja"
)

RENAME_PROJECT=(
    "$TEMPLATE_DIR/src/fractal_tasks_template"
    "$TEMPLATE_DIR/src/{{package_name}}"
)

ALL_RENAMES=(
    "${RENAME_TASK_SCRIPT[@]}"
    "${RENAME_DOC[@]}"
    # "${RENAME_PROJECT[@]}"
)

# File names to be templatized (i.e., where keywords will be inserted in the file names)

# End of safe zone
TMP_DIR="_tmp"
TEMPLATE_FILES=(
    "{{_copier_conf.answers_file}}.jinja"
    "{% if project_license == 'Apache-2.0' %}LICENSE{% endif %}.jinja"
    "{% if project_license == 'BSD-3-Clause' %}LICENSE{% endif %}.jinja"
    "{% if project_license == 'GPL-3.0' %}LICENSE{% endif %}.jinja"
    "README.md.jinja"
)

# Script starts here

# Step 1: Clean up current template dir

# clean up template dir by removing all files not starting with '{'
# and all empty directories
echo "[build_template.sh] Cleaning up template directory."

mkdir -p "$TMP_DIR"
for file in "${TEMPLATE_FILES[@]}"; do
    cp "$SOURCE_DIR/template/$file" "$TMP_DIR/"
done

rm -rf "$TEMPLATE_DIR"
mkdir -p "$TEMPLATE_DIR"

for file in "${TEMPLATE_FILES[@]}"; do
    cp "$TMP_DIR/$file" "$TEMPLATE_DIR/"
done

rm -rf "$TMP_DIR"

# Step 2: Copy relevant files from SOURCE_DIR to TEMPLATE_DIR
# and remove unwanted files and directories
echo "[build_template.sh] Copying relevant files from $SOURCE_DIR to $TEMPLATE_DIR"
for item in "${TO_COPY[@]}"; do
    echo "[build_template.sh] Copying $item to $TEMPLATE_DIR"
    cp -r "$item" "$TEMPLATE_DIR/"
done

for item in "${TO_BE_REMOVED[@]}"; do
    echo "[build_template.sh] Removing $item from $TEMPLATE_DIR"
    rm -rf "$item"
done

# Step 3: Remove rename the extension of files to be templatized to .jinja
echo "[build_template.sh] Templatizing files."
for file in "${FILES_TO_TEMPLATIZE[@]}"; do
    mv "$file" "$file.jinja"
done

# Step 4: Rename keywords to be replaced in files with their jinja2 template equivalents
# Replace keywords in files
for ((i=0; i<${#KEYWORD_MAP[@]}; i+=2)); do
    echo "[build_template.sh] Replacing '${KEYWORD_MAP[i]}' with '${KEYWORD_MAP[i+1]}' in files."
    for file in "${FILES_TO_TEMPLATIZE[@]}"; do
        # Replace inside jinja files
        file="$file.jinja"
        search="${KEYWORD_MAP[i]}"
        replace="${KEYWORD_MAP[i+1]}"
        sed -i.bak "s/$search/$replace/g" "$file"
    done
done


# Step 5: Rename files and directories to include jinja2 templates
# Rename files and directories
for ((i=0; i<${#ALL_RENAMES[@]}; i+=2)); do
    old_name="${ALL_RENAMES[i]}"
    new_name="${ALL_RENAMES[i+1]}"
    #destdir="$(dirname "$new_name")"
    #mkdir -p "$destdir"
    mv "$old_name" "$new_name"
    rm -rf "$old_name"
    echo "[build_template.sh] Renamed '$old_name' to '$new_name'."
done

# Step 6: Clean up backup files created by sed
# Clean up backup files created by sed
find "$TEMPLATE_DIR" -name "*.bak" -type f -delete
echo "[build_template.sh] Removed backup files created by sed."