# Story: Automate Release Process

## 関連Issue (Relation)
- This Story is part of **Epic: Implement ADR-010 CI/CD Process Improvements**

## As-is (現状)
The release process, including version bumping, CHANGELOG generation, and GitHub release creation, is entirely manual.

## To-be (あるべき姿)
The release process is fully automated using `python-semantic-release`, triggered by merges to the `main` branch.

## 完了条件 (Acceptance Criteria)
- [ ] `python-semantic-release` is added as a development dependency.
- [ ] The project is configured to use `python-semantic-release`, including custom rules for `epic:` (minor) and `story:` (patch) commit types.
- [ ] The CI workflow is updated to include a step for validating commit messages against the Conventional Commits standard.
- [ ] Developer documentation is updated to explain the new requirement for Conventional Commits.

## 成果物 (Deliverables)
- `pyproject.toml` (or equivalent configuration file)
- `.github/workflows/ci.yml`
- `CONTRIBUTING.md` (or `docs/guides/development-workflow.md`)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-010`
- **作業ブランチ (Feature Branch):** `story/automate-release-process`
