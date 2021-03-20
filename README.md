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

This repository uses PGA Shotlink Data to infer the ideal locations to hit golf shots on the PGA Tour. A user can select a tournament, and for each hole, analyse the shot distribution on a given hole that lead to a sub-, even-, or over-par score for all pin locations.

The data comes from a test set of PGA Shotlink data, from the GitHub repo [pga-golf-data](https://github.com/brendansudol/pga-golf-data/). This is added as a submodule in `third-party`. Ensure to initialise the submodules appropriately.

## Installation & Usage

## Running

For this repository to function as intended, a few tools have been provided to ensure the application can be containerised and sent to the appropriate container repository.

### Makefile

The content of the `Makefile` should only be modified if the standard behaviour is not achieved using the default. Standard commands are as follows:

| Command | Dependencies | Action | Image Tag (local and remote)
----------------------|---|---|---
`make run` | `run` | Runs image | Git commit's tag, otherwise `latest`
`make build` | `build` | Builds image | `custom_tag`

### Scripts

The `scripts` folder must maintain the following, which are indirectly run from the Makefile in the root directory. The `build` script is customizable per the  application, but it must build a local image of the application which can be uploaded the container repository for use in the cluster pipeline. The `upload` script **should not be modified**. The `run` script is listed as an empty placeholder script, and commented code is included in the Makefile to show how to integrate a `run` script into the code repository. The operation of the `run` scripts are application specific and do not need to share common functionality at this time.

| Script   | Inputs |Output|
|----------|------ |---
| build.sh  | NAME TAG | Application image is created locally, tagged with input args |
| upload.sh | NAME TAG | Application image is uploaded to container repository, tagged with input args |
| run.sh    | NAME TAG | Application image is run locally |

### Development or Production

For now, use the docker-compose file to spin up the application and the nginx server. Run `docker-compose up --build`. The application is available at `localhost`, `127.0.0.1` on the local machine, or the IP address of the machine, if accessed from another computer on the network. `nginx.conf` needs to be configured appropriately.

For development, simply run `make run` and the development environment will start.

## Contributing
The guidelines for contributing are laid out here.


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
