"""Contains the list of tasks available to fractal."""

from fractal_task_tools.task_models import (
    ParallelTask,
)

AUTHORS = "Fractal Core Team"
DOCS_LINK = None
INPUT_MODELS = [
    ("ngio", "images/_image.py", "ChannelSelectionModel"),
    (
        "fractal_tasks_template",
        "utils.py",
        "MaskingConfiguration",
    ),
    (
        "fractal_tasks_template",
        "utils.py",
        "IteratorConfiguration",
    ),
]

TASK_LIST = [
    # --- #{% if include_segmentation_tasks %}
    ParallelTask(
        name="Example Segmentation Task",
        executable="example_segmentation_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Segmentation",
        tags=["Instance Segmentation", "Classical segmentation"],
        docs_info="file:docs_info/example_segmentation_task.md",
    ),
    # --- #{% endif %}
]
