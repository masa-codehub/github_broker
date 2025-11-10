# 目的とゴール / Purpose and Goals
Task: Add commit message validation to CI

## Status
**COMPLETED** on 2025-10-19

## 親Issue (Parent Issue)
- Story: Automate Release Process

## As-is (現状)
CIはコミットメッセージがConventional Commits規約に準拠しているかを検証していません。

## To-be (あるべき姿)
CIワークフローにコミットメッセージを検証するステップが追加され、規約違反のコミットがマージされるのを防ぎます。

## 完了条件 (Acceptance Criteria)
- [x] `.github/workflows/ci.yml`に、コミットメッセージがConventional Commits規約に従っているかをチェックするステップ（例: `commitlint`を使用）が追加されていること。

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## 影響範囲と今後の課題 / Impact and Future Issues

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/automate-release-process`
- **作業ブランチ (Feature Branch):** `task/add-commit-message-validation-to-ci`

## 担当エージェント (Agent)
- BACKENDCODER

## 優先度 (Priority)
- P0

# Issue: #1462

## 子Issue (Sub-Issues)
