# Task: Add commit message validation to CI

## 親Issue (Parent Issue)
- Story: Automate Release Process

## As-is (現状)
CIはコミットメッセージがConventional Commits規約に準拠しているかを検証していません。

## To-be (あるべき姿)
CIワークフローにコミットメッセージを検証するステップが追加され、規約違反のコミットがマージされるのを防ぎます。

## 完了条件 (Acceptance Criteria)
- [ ] `.github/workflows/ci.yml`に、コミットメッセージがConventional Commits規約に従っているかをチェックするステップ（例: `commitlint`を使用）が追加されていること。

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/automate-release-process`
- **作業ブランチ (Feature Branch):** `task/add-commit-message-validation-to-ci`
