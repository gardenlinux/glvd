# Garden Linux Vulnerability Database

This repository contains the Security Tracker of Garden Linux. The Security Tracker is called `glvd` and it is an application written in Python that is operated within a Debian testing container. By offering a container image, the Security Tracker can simply be operated on any machine via tools like `docker` or `podman` but it could also be used for container orchestration tools like Kubernetes in order to run it at scale.

More information about the infrastructure on which `glvd` will be operated, can be found here:
* https://github.com/gardenlinux/glvd-infrastructure

This repository on the other hand contains the actual source code of the Security Tracker.

## Repository Structure
Thereby, this repostory contains the following directories:

- `docs/`: This directory contains documentation regarding `glvd`.
- `src/`: This directory contains the source files of `glvd`.
  - `glvd/`: The main directory of the Security Tracker.
    - `cli/`: Command Line Interface for running operational tasks on `glvd`.
    - `data/`: The backend implementation for dealing with the Security Tracker data like CPEs, CVEs and Debian Sources.
    - `database/`: Contains the sqlalchemy classes for representing each table used by `glvd`.
    - `web/`: The actual web application and its endpoint that can be called to receive vulnerabilities from the Security Tracker. This code represents the API.
- `tests/`: This directory contains all tests (e.g. unit tests) used by pytest regarding `glvd`.

Other important files are:
- [Containerfile](./Containerfile): This file specifies the corresponding container of `glvd`.
- [openapi-v1.yaml](./openapi-v1.yaml): This configuration defines the API endpoints of `glvd`.
- [pyproject.toml](./pyproject.toml): The configuration file for defining the Python project / application.
- [setup.cfg](./setup.cfg): Configuration file for defining the metadata of the Python project typically used by setuptools.

## Documentation

### Client

The client documentation can be found here: [docs/01_client.md](./docs/01_client.md)

### Server


### Ingestion
