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

---

## Stories

### Story 1: Unify and Accelerate Quality Checks

- **Status:** Not Created
- **Priority:** P0
- **As-is:** CI runs linting, formatting, and testing in separate, slow steps.
- **To-be:** A single, unified CI step runs all quality checks in parallel, significantly reducing feedback time.
- **完了条件:**
    - [ ] `pytest-xdist` is added as a development dependency.
    - [ ] The `.pre-commit-config.yaml` is updated to run `pytest` with the `-n auto` option.
    - [ ] The `.github/workflows/ci.yml` file is refactored to use a single `pre-commit run --all-files` command for all checks.
- **成果物:**
    - `pyproject.toml` (or `requirements.in`)
    - `.pre-commit-config.yaml`
    - `.github/workflows/ci.yml`
- **ブランチ戦略:**
    - **ベースブランチ:** `epic/implement-adr-010`
    - **作業ブランチ:** `story/unify-and-accelerate-checks`

### Story 2: Automate Release Process

- **Status:** Not Created
- **Priority:** P1
- **As-is:** The release process, including version bumping, CHANGELOG generation, and GitHub release creation, is entirely manual.
- **To-be:** The release process is fully automated using `python-semantic-release`, triggered by merges to the `main` branch.
- **完了条件:**
    - [ ] `python-semantic-release` is added as a development dependency.
    - [ ] The project is configured to use `python-semantic-release`, including custom rules for `epic:` (minor) and `story:` (patch) commit types.
    - [ ] The CI workflow is updated to include a step for validating commit messages against the Conventional Commits standard.
    - [ ] Developer documentation is updated to explain the new requirement for Conventional Commits.
- **成果物:**
    - `pyproject.toml` (or equivalent configuration file)
    - `.github/workflows/ci.yml`
    - `CONTRIBUTING.md` (or `docs/guides/development-workflow.md`)
- **ブランチ戦略:**
    - **ベースブランチ:** `epic/implement-adr-010`
    - **作業ブランチ:** `story/automate-release-process`
