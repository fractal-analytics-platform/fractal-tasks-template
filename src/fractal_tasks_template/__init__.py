"""Package description."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fractal_tasks_template")
except PackageNotFoundError:
    __version__ = "uninstalled"
