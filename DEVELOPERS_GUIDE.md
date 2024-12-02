## Development instructions

These instructions are only relevant *after* you completed both the `copier
copy` command and the git/GitLab/GitHub initialization phase - see
[README](https://github.com/fractal-analytics-platform/fractal-tasks-template#readme)
for details.

### Getting started

1. It is recommended to work from an isolated Python virtual environment, we suggest using `mamba` to create the environment. You can install it via [miniforge](https://github.com/conda-forge/miniforge).

2. Once you have `mamba` installed, you can create the virtual environment using the following command:
```console
mamba create -n name-env python=3.10
```
Here we used python 3.10 as an example, you can alternatively use `python=3.9` or `python=3.11`.
In order to use the conda environment, you need to activate it:
```console
mamba activate name-env
```
and once you are done with the environment, you can deactivate it:
```console
mamba deactivate
```
or, simply close the terminal.

3. You can install your package to run it locally as in (run from within your package folder):
```console
python -m pip install -e .
```
this will install only the dependencies needed to run the package. If you want to install the development dependencies (e.g. pytest, hatch), you can run:
```console
python -m pip install -e ".[dev]"
```
## Task development instructions
1. The template already includes a sample task ("Thresholding Label Task"). Whenever you change its input parameters or docstring, re-run
```console
python src/{{package_name}}/dev/create_manifest.py
git add src/{{package_name}}/__FRACTAL_MANIFEST__.json
git commit -m 'Update `__FRACTAL_MANIFEST__.json`'
git push origin main
```

2. A full walkthrough of the task development process can be found in the [Build your own fractal task](https://fractal-analytics-platform.github.io/build_your_own_fractal_task/) documentation & video tutorial.

3. If you add a new task, you should also add a new item to the `TASK_LIST`
list, in `src/{{package_name}}/dev/task_list.py`. Here is an example:
```python
from fractal_tasks_core.dev.task_models import NonParallelTask
from fractal_tasks_core.dev.task_models import ParallelTask
from fractal_tasks_core.dev.task_models import CompoundTask


TASK_LIST = [
    NonParallelTask(
        name="My non-parallel task",
        executable="my_non_parallel_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Conversion",
        modality="HCS",
    ),
    ParallelTask(
        name="My parallel task",
        executable="my_parallel_task.py",
        meta={"cpus_per_task": 1, "mem": 4000},
        category="Image Processing",
        tags=["Preprocessing"],
    ),
    CompoundTask(
        name="My compound task",
        executable_init="my_task_init.py",
        executable="my_actual_task.py",
        meta_init={"cpus_per_task": 1, "mem": 4000},
        meta={"cpus_per_task": 2, "mem": 12000},
        category="Segmentation",
        tags=[
            "Deep Learning",
            "Convolutional Neural Network",
            "Instance Segmentation",
        ],
    ),
]
```

6. Add task metadata
To make sure that other Fractal users can find your task it's essential to fill the metadata in the `TASK_LIST`

Allowed metadata are:

* Category (Optional): The type of task implemented. Possible standard choices are "Segmentation," "Conversion," "Image Processing," and "Registration."
* Modality (Optional): The type of data modality supported, for example, "HCS".
* Tags (Optional): A free list of additional tags assigned to your data.

Notes:

* After adding a task, you should also update the manifest (see point 1/ above).
* The minimal example above also includes the `meta` and/or `meta_init` task properties; these are optional, and you can remove them if not needed.

## Testing
1. Run the test suite (with somewhat verbose logging) through
```console
python -m pytest --log-cli-level info -s
```

* The template already includes some sample tests to verify the correctness of the tasks, and some tests to verify the correctness of the `__FRACTAL_MANIFEST__.json` file.

## Versioning
We encourage the use of [Semantic Versioning](https://semver.org/). 
To update the version of your package, you can use the following command:
```console
git tag -a va.b.c -m 'Name of the release'
```
where `a`, `b`, `c` are the major, minor and patch version numbers respectively.

You can also add tags directly on Github.

Upon a tag push, a special CI pipeline will be triggered, which will build the package and upload the wheel in your repository's `releases` section.
When you are ready to publish your package on PyPI, you can do so by creating a new PyPI project and removing the line `if: false` from the `Publish to PyPI` step in `build_and_test.yml`.

Note that this requires some preliminary steps on PyPI, like setting up an account, creating a project, and setting up a "trusted publisher" that links your repository to PyPI - see https://docs.pypi.org/trusted-publishers.

## Building the package

In order to build the package, use `hatch`. You can build the package by running the following command:
```console
hatch build
```
This command will create the release distribution files in the `dist` folder.
The wheel one (ending with `.whl`) is the one you can use to collect your tasks
within Fractal.

## Pre-commit
This template uses `pre-commit` to run some checks before committing your changes. You set up pre-commit it via:
```console
pre-commit install
```
This will install the pre-commit hooks in your `.git/hooks` directory, and they will run every time you commit changes.
This is particularly useful when working with other people, as it ensures that the code is formatted homogeneously.
