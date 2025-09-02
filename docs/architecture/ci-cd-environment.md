# CI/CD Environment

This document outlines the specifications of the self-hosted runner environment used for Continuous Integration (CI) and Continuous Deployment (CD).

## Runner Specifications

Our CI/CD pipeline utilizes a self-hosted runner with the following configuration:

- **Labels:** `self-hosted`, `linux`, `x64`, `gpu`
- **Host Environment:** The runner is hosted within a `github-runner` container.

## Usage

When creating or modifying GitHub Actions workflows, jobs that need to run in this environment must specify the correct labels in the `runs-on` directive:

```yaml
jobs:
  my-job:
    runs-on: [self-hosted, linux, x64, gpu]
    steps:
      - ...
```
