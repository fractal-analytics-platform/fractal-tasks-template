# Fractal tasks-package template

This is a template for a Python package of tasks that can be used within [the
Fractal framework](https://fractal-analytics-platform.github.io/). This
template is largely inspired by https://github.com/pydev-guide/pyrepo-copier.

## How to use it

### Requirements
* `copier`: This template uses [`copier`](https://copier.readthedocs.io) to create a new
   repository from the template. You can install it e.g. via [`pipx`](https://pypa.github.io/pipx), as in
   ```console
   pipx install copier
   ```
* `git` (Optional): The template includes a post-copy script that initializes a git repository.
   If you never used `git` before, you might need to first [install it](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   and configure an user name and email, as in
   ```console
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
* `pixi` (Optional): The template includes a post-copy script that uses `pixi` to create a Python environment, and run
   some formatting and pytest to make sure everything is working. 
   If you don't want to use `pixi`, you can skip this step and manually create a Python environment with your favorite tools.
   If you want to get started with `pixi` following the instructions in [pixi's documentation](https://pixi.sh/latest/installation/).

### 1. Copy and customize the template (first-time only)

Then run `copier`, passing in the template url and the desired
output directory (usually the name of your new package):
```console
copier copy gh:fractal-analytics-platform/fractal-tasks-template your-package-name --trust
```

As part of this procedure, `copier` will ask you a set of questions; answers
are used to customize the template to fit your needs (e.g. by setting
appropriate file/folder names).

The `--trust` flag is needed to run the post-copy script that initializes
the package structure.

The post-copy script will:
1. Initialize a git repository.
2. Use `pixi` to create a Python environment, and run some formatting and pytest to make sure everything is working.

The script can be safely skipped by answering "no" when asked by `copier`.

### Manual post-install: Initialize `git`/GitLab/GitHub repository

If you skipped the post-copy script, you need to manually initialize a `git` repository.
This step is required because in this template, we use git tags to manage the versioning of the package.

You can create a `git` repository based on the current folder via
```console
cd <your-package-name>
git init
git add .
git commit -m 'Initial commit'
```
Then you can create a first tag, e.g. for version 0.1.0, via
```console
git tag -a 0.1.0 -m 'Initial version'
```

This is enough for local tracking of your package, but you may want to also keep a remote copy of your repository. To do so in GitLab or GitHub, for instance, follow the instructions in:
* GitLab: [Convert a local directory into a repository](https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html#convert-a-local-directory-into-a-repository)
* GitHub: [Adding a local repository to GitHub using Git](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github#adding-a-local-repository-to-github-using-git)

### 2. Start developing

Your customized instance of the template is now ready, and you can start
developing. Specific instructions on how to install your package, managing your environment, versioning and more can be found in the [DEVELOPERS_GUIDE](https://github.com/fractal-analytics-platform/fractal-tasks-template/blob/main/DEVELOPERS_GUIDE.md).

### 3. Fetch template updates

This template may change over time, bringing in new improvements, fixes, and
updates. To update an existing project that was created from this template
using `copier`, follow these steps:
```console
# From the root folder of your repository
cd <your-package-name>

# Run `git status` and make sure its output looks like
# >> "nothing to commit, working tree clean"
git status

# Run the update
copier update
```
See [copier docs](https://copier.readthedocs.io/en/stable/updating) for more
details.

## Contributing

Contributions to this template are welcome!

The `template` directory contains the actual template files, with will be used by `copier` to create new repositories. 
This directory should not be modified manually. But it is automatically created by running
```console
pixi run python src/build_template/main.py
```

