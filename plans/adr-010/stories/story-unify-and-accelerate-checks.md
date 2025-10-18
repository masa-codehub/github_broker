# Story: Unify and Accelerate Quality Checks

## 関連Issue (Relation)
- This Story is part of **Epic: Implement ADR-010 CI/CD Process Improvements**

## As-is (現状)
CI runs linting, formatting, and testing in separate, slow steps.

## To-be (あるべき姿)
A single, unified CI step runs all quality checks in parallel, significantly reducing feedback time.

## 完了条件 (Acceptance Criteria)
- [ ] `pytest-xdist` is added as a development dependency.
- [ ] The `.pre-commit-config.yaml` is updated to run `pytest` with the `-n auto` option.
- [ ] The `.github/workflows/ci.yml` file is refactored to use a single `pre-commit run --all-files` command for all checks.

## 成果物 (Deliverables)
- `pyproject.toml` (or `requirements.in`)
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-010`
- **作業ブランチ (Feature Branch):** `story/unify-and-accelerate-checks`
