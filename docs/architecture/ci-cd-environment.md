# CI/CD Environment

This document outlines the specifications of the self-hosted runner environment used for Continuous Integration (CI) and Continuous Deployment (CD).

## Runner Specifications

Our CI/CD pipeline utilizes a self-hosted runner with the following configuration:

- **Labels:** `self-hosted`, `linux`, `x64`, `gpu`
- **Operating System:** Ubuntu 24.04
- **GPU:** 不明
- **Host Environment:** The runner is hosted within a `github-runner` container using the `github_broker-github_runner` image.

## CI Trigger

Continuous Integration (CI) is triggered on **all Pull Requests** regardless of the target branch. This ensures that all feature branches are validated before merging, improving code quality and reducing the risk of introducing bugs into the main development line.

## Usage

When creating or modifying GitHub Actions workflows, jobs that need to run in this environment must specify the correct labels in the `runs-on` directive:

```yaml
jobs:
  my-job:
    runs-on: [self-hosted, linux, x64, gpu]
    steps:
      - ...
```
