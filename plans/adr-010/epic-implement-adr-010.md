# Epic: Implement ADR-010 CI/CD Process Improvements

## 関連Issue (Relation)
- This Epic implements [ADR-010: CI/CD Process Improvement](../../docs/adr/010-ci-cd-process-improvement.md).

## As-is (現状)
The current CI/CD process involves multiple, slow, and separate steps for linting, testing, and formatting. The release process is manual, error-prone, and time-consuming.

## To-be (あるべき姿)
A streamlined, fast, and automated CI/CD pipeline. A single, fast `pre-commit` job validates all code changes, and the release process is fully automated based on Conventional Commits.

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryが完了すること。
  - [ ] Story: Unify and Accelerate Quality Checks
  - [ ] Story: Automate Release Process

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-010`

# Issue: #1455
