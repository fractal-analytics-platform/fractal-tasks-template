"""This script builds the template directory for the fractal-tasks-template project.

Replicates the original bash script's behavior:
1) Clean & seed the template directory with static template files
2) Copy selected project files/dirs into template/
3) Convert selected files to .jinja
4) Apply string replacements inside those files
5) Rename files/dirs to include jinja placeholders
6) Cleanup backup files

Usage:
    python build_template.py
"""

import argparse
import shutil
import subprocess
import sys
from collections.abc import Generator
from itertools import product
from pathlib import Path

import yaml

# ---- Constants and variables (safe zone to edit) ----

source_dir = Path(".")  # Directory containing the source files to build the template
template_dir = Path("template")  # Directory where the template will be built
static_template_dir = Path("static_template")  # Directory with static files to copy

# These files and directories will be copied from SOURCE_DIR to TEMPLATE_DIR
to_be_included = [
    "src",
    "tests",
    "pyproject.toml",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".github",
]

# These files and directories will be removed from TEMPLATE_DIR after copying
to_be_excluded = [
    Path("src") / "build_template",
    Path("tests") / "copier",
    Path(".github") / "workflows" / "copier_ci.yml",
    Path(".github") / "workflows" / "github_release.yaml",
    Path(".github") / "workflows" / "github_release.yml",
]

# End of editable zone

# Patterns to exclude when listing files
_exclusion_patterns = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "__pycache__",
    ".DS_Store",
    ".ipynb_checkpoints",
]

# Additional mappings that are not in keywords_map.yml
_fix_mappings = {
    "{{ '{{' }}  matrix.python-version {{ '{{' }} }}": "{{ matrix.python-version }}",
    "{{ '{{' }}  matrix.os {{ '{{' }} }}": "{{ matrix.os }}",
    "": "# --- #",  # Special marker to uncomment lines
}

# ---- Helpers ----


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build the template directory.")

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to the YAML configuration file for keyword mappings",
        default=Path("keywords_map.yml"),
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if the template is up to date (git diff)",
        default=False,
    )
    return parser.parse_args()


def print_log(msg: str) -> None:
    """Log a message to stdout with a prefix."""
    print(f"[build_template.py] {msg}")


def path_generator(root: Path) -> Generator[Path, None, None]:
    """Generate all files and directories under root, excluding certain patterns."""
    for path in root.rglob("*"):
        if any(path.match(pattern) for pattern in _exclusion_patterns):
            continue
        yield path


def copy_any(src: Path, dst_dir: Path) -> None:
    """Copy a file or directory into dst_dir, preserving metadata."""
    if not src.exists():
        print_log(f"WARNING: {src} does not exist; skipping.")
        return
    dst = dst_dir / src.name
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, dirs_exist_ok=False)
    else:
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def ensure_removed(path: Path) -> None:
    """Remove a file or directory if it exists."""
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink(missing_ok=True)


def replace_in_file(path: Path, search: str, replace: str) -> bool:
    """Replace all occurrences of 'search' with 'replace' in the file at 'path'."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    text = path.read_text(encoding="utf-8")
    if search in text:
        print_log(f"Replacing '{search}' with '{replace}' in {path}")
        new_text = text.replace(search, replace)
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def move_path(old: Path, new: Path) -> None:
    """Rename a file or directory from 'old' to 'new'."""
    if not old.exists():
        print_log(
            f"WARNING: Cannot rename '{old}' -> '{new}' "
            "because source is missing; skipping."
        )
        return
    new.parent.mkdir(parents=True, exist_ok=True)
    # If new exists and is a dir, remove it before move to mimic mv behavior used here
    if new.exists():
        if new.is_dir():
            shutil.rmtree(new)
        else:
            new.unlink()
    shutil.move(str(old), str(new))


# ---- Main workflow ----


def main(args: argparse.Namespace) -> int:
    """Main function to build the template directory."""
    # Load keyword mappings from YAML file
    if not args.config.exists():
        raise FileNotFoundError(f"Configuration file not found: {args.config}")

    with args.config.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    keyword_map: dict[str, str] = config["keyword_map"]

    conditional_patterns: dict[str, str] = config["conditional_patterns"]
    # Step 1: Clean up current template dir
    print_log("Cleaning up template directory.")
    if template_dir.exists():
        shutil.rmtree(template_dir)
    template_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Copy relevant files from SOURCE_DIR to TEMPLATE_DIR
    print_log(f"Copying relevant files from {source_dir} to {template_dir}")
    for item in to_be_included:
        print_log(f"Copying {item} to {template_dir}")
        static_file = source_dir / item
        copy_any(static_file, template_dir)

    for item in to_be_excluded:
        print_log(f"Removing {item} from {template_dir}")
        static_file = template_dir / item
        ensure_removed(static_file)

    # Step 4: Replace keywords in files
    path_changed = []
    for key, search in keyword_map.items():
        for static_file in path_generator(template_dir):
            replace = "{{ " + key + " }}"
            if static_file.is_file() and replace_in_file(static_file, search, replace):
                path_changed.append(static_file)

    for replace, search in _fix_mappings.items():
        for static_file in path_generator(template_dir):
            if static_file.is_file() and replace_in_file(static_file, search, replace):
                path_changed.append(static_file)

    # Step 5: Rename files and directories to include jinja placeholders
    for static_file in set(path_changed):
        # Change extension to .jinja if it is not already a .jinja file
        if not static_file.suffix == ".jinja":
            new_file = static_file.with_suffix(static_file.suffix + ".jinja")
            move_path(static_file, new_file)
            print_log(f"Jinjified {static_file} -> {new_file}")

    while True:
        # Repeat until no more renames are done
        pairs = product(path_generator(template_dir), keyword_map.items())
        for static_file, (key, search) in pairs:
            if search in static_file.name:
                print(f"Found {search} in {static_file.name}")
                replace = "{{ " + key + " }}"
                new_name = static_file.name.replace(search, replace)
                new_path = static_file.parent / new_name
                move_path(static_file, new_path)
                print_log(f"Renamed {static_file} -> {new_path}")
                break
        else:
            break

    # Step 6: Remove conditional files if conditions are not met
    for search, condition in conditional_patterns.items():
        for static_file in path_generator(template_dir):
            if search in static_file.name:
                new_stem = (
                    "{% if " + condition + " %}" + static_file.stem + "{% endif %}"
                )
                new_name = new_stem + ".jinja"
                new_path = static_file.parent / new_name
                move_path(static_file, new_path)
                print_log(f"Renamed {static_file} -> {new_path}")

    # Move static template files
    current_files = set(path_generator(template_dir))
    for static_file in path_generator(static_template_dir):
        if static_file.is_dir():
            raise NotImplementedError(
                "Directory structures in static_template_dir are not supported."
            )

        for file in current_files:
            if file.name == static_file.name:
                print_log(f"Replacing existing file {file} with static template file.")
                destination = file.parent
                file.unlink()
                break
        else:
            destination = template_dir
            print_log(f"Copying new static template file {static_file}.")
        copy_any(static_file, destination)

    # Final cleanup removing any #---# special markers left in files
    print_log("Build complete.")

    if args.check:
        # Use git diff to check if the template hasn't changed
        result = subprocess.run(
            ["git", "diff", "--exit-code", str(template_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print_log("Check failed: template directory has changed.")
            return 1
        print_log("Check succeeded: template directory is up to date.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
