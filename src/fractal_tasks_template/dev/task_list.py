"""Contains the list of tasks available to fractal."""

from fractal_task_tools.task_models import (
    ParallelTask,
)

AUTHORS = "Fractal Core Team"
DOCS_LINK = "project_url.uzh.ch"
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
    # --- #{% if include_segmentation_task %}
    ParallelTask(
        name="Threshold Segmentation",
        executable="threshold_segmentation_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Segmentation",
        tags=["Instance Segmentation", "Classical segmentation"],
        docs_info="file:docs_info/threshold_segmentation_task.md",
    ),
    # --- #{% endif %}
    # --- #{% if include_image_processing_task %}
    ParallelTask(
        name="Gaussian Blur",
        executable="gaussian_blur_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Image Processing",
        tags=["Denoising", "Gaussian Blur"],
        docs_info="file:docs_info/gaussian_blur_task.md",
    ),
    # --- #{% endif %}
    # --- #{% if include_feature_task %}
    ParallelTask(
        name="Region Props Features",
        executable="region_props_features_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Measurement",
        tags=["Region Properties", "Intensity", "Morphology"],
        docs_info="file:docs_info/region_props_features_task.md",
    ),
    # --- #{% endif %}
]
