# Epic: Implement ADR-010 CI/CD Process Improvements

## 関連Issue (Relation)
- This Epic implements [ADR-010: CI/CD Process Improvement](../../docs/adr/010-ci-cd-process-improvement.md).

## As-is (現状)
The current CI/CD process involves multiple, slow, and separate steps for linting, testing, and formatting. The release process is manual, error-prone, and time-consuming.

## To-be (あるべき姿)
A streamlined, fast, and automated CI/CD pipeline. A single, fast `pre-commit` job validates all code changes, and the release process is fully automated based on Conventional Commits.

## 完了条件 (Acceptance Criteria)
- The CI workflow log shows that `pre-commit run --all-files` is executed, and lint, format, type, and test checks are successful.
- The CI test execution step log confirms that tests are run in parallel by `pytest-xdist`.
- Merging a PR with a `feat:` or `fix:` commit to `main` automatically creates a new versioned GitHub release via `python-semantic-release`.
- Merging a commit with `epic:` increments the minor version, and `story:` increments the patch version.

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-010`
