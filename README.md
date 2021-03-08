<p align="center">
<a href="https://github.com/psf/black"><img alt="code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://gitlab.com/PyCQA/flake8"><img alt="code style: flake8" src="https://img.shields.io/badge/code%20style-pep8-orange.svg"></a>
<a href="https://github.com/PyCQA/bandit"><img alt="security: bandit" src="https://img.shields.io/badge/security-bandit-yellow.svg"></a>
<a href="https://github.com/pre-commit/pre-commit"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit" style="max-width:100%;"></a>
</p>

---

_Contents:_
**[Background](#background)** |
**[Installation](#installation)** |
**[Running](#running)** |
**[Contributing](#contributing)** |

---

## Background

This repository has been developed as a common starting point for application development. It has a standard structure and common set of tooling to ensure accuracy and consistency across all applications.

Naming conventions for repositories:

| Valid | Invalid |
|---|---|
|`-`, Capital Letters, Lowercase Letters | `_`
|---|---|
|A-Legitimate-Repository | an_illegitemate_repository

## Installation & Usage

1. From this repository, click the "Use this template" button.
2. Name your repository appropriately (see [Background](#Background)).
3. Clone the new repository and navigate to its directory.
4. Run the starup script `start_new_repo.sh`, which will:
  	- initialise the submodule,
  	- push the modified repository to Github, then
  	- delete the script.

Once this is done, you are ready to start development of your new application.

Ensure you update the Background and Installation & Usage sections so that they relate to your application.

## Running

For this repository to function as intended, a few tools have been provided to ensure the application can be containerised and sent to the appropriate container repository.

### Makefile

The content of the `Makefile` should only be modified if the standard behaviour is not achieved using the default. Standard commands are as follows:

| Command | Dependencies | Action | Image Tag (local and remote)
----------------------|---|---|---
`make publish` | `build upload` | Builds and uploads image | Git commit's tag, otherwise `latest`
`make publish TAG=custom_tag` | `build upload` | Builds and uploads image | `custom_tag`

### Scripts

The `scripts` folder must maintain the following, which are indirectly run from the Makefile in the root directory. The `build` script is customizable per the  application, but it must build a local image of the application which can be uploaded the container repository for use in the cluster pipeline. The `upload` script **should not be modified**. The `run` script is listed as an empty placeholder script, and commented code is included in the Makefile to show how to integrate a `run` script into the code repository. The operation of the `run` scripts are application specific and do not need to share common functionality at this time.

| Script   | Inputs |Output|
|----------|------ |---
| build.sh  | NAME TAG | Application image is created locally, tagged with input args |
| upload.sh | NAME TAG | Application image is uploaded to container repository, tagged with input args |
| run.sh    | NAME TAG | Application image is run locally |

## Contributing
The guidelines for contributing are laid out here. All members of the team have write access.

### Development Environment
- Install [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) for creating a nice virtual container to run in.
- See [Running](#Running).

### Testing
No untested code will be allowed to merge onto Master. A 90% coverage and test passing report is required for all Master PRs.

#### Using PyTest
This library uses pytest for testing. To run the full test suite use the command `pytest tests/ --cov=lib --cov-report=html`.

### Code Style
Code style is handled and enforced with [Black](https://github.com/psf/black), [Flake8](https://gitlab.com/pycqa/flake8) and some additional stylers and formatters. A pre-commit hook is provided with this repository so that all code is automatically kept consistent. If there are any issues with formatting, please submit a formal PR to this repository.

Docstrings will be formatted according to the Google docstring formatting, and as best as possible, styled as per the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
