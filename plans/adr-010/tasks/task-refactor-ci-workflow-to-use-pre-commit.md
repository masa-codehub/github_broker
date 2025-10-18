# Task: Refactor CI workflow to use pre-commit

## 親Issue (Parent Issue)
- Story: Unify and Accelerate Quality Checks

## As-is (現状)
CIワークフローは、lint、format、testを個別のステップとして実行しており、冗長です。

## To-be (あるべき姿)
CIワークフローがリファクタリングされ、`pre-commit run --all-files`を実行する単一のジョブに集約されます。これにより、ローカルとCIのチェックが完全に一致します。

## 完了条件 (Acceptance Criteria)
- [ ] `.github/workflows/ci.yml`から、lint、format、testの個別ステップが削除され、`pre-commit run --all-files`を実行するステップに置き換えられていること。

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/unify-and-accelerate-checks`
- **作業ブランチ (Feature Branch):** `task/refactor-ci-workflow-to-use-pre-commit`

## 担当エージェント (Agent)
- BACKENDCODER

## 優先度 (Priority)
- P0

# Issue: #1460
