# CI/CD Environment

This document outlines the specifications of the self-hosted runner environment used for Continuous Integration (CI) and Continuous Deployment (CD).

## Runner Specifications

Our CI/CD pipeline utilizes a self-hosted runner with the following configuration:

- **Labels:** `self-hosted`, `linux`, `x64`, `gpu`
- **Operating System:** Ubuntu 24.04
- **GPU:** 不明
- **Host Environment:** The runner is hosted within a `github-runner` container using the `github_broker-github_runner` image.

## CI Triggers

継続的インテグレーション (CI) は、ターゲットブランチに関わらず、コード変更を含むすべてのプルリクエストでトリガーされます。ただし、ドキュメント（`.md`ファイルや`docs/`、`plans/`配下のファイル）のみの変更では、CIの実行はスキップされます。これにより、すべてのフィーチャーブランチがマージ前に検証され、コードの品質が向上し、メインの開発ラインにバグが混入するリスクが低減されます。

## Usage

When creating or modifying GitHub Actions workflows, jobs that need to run in this environment must specify the correct labels in the `runs-on` directive:

```yaml
jobs:
  my-job:
    runs-on: [self-hosted, linux, x64, gpu]
    steps:
      - ...
```
