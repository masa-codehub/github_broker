# Issue: #1517
Status: Open
# 【Story】CIワークフローが全ブランチへのPRでトリガーされるようにする

## 親Issue (Parent Issue)
- #1516

## 子Issue (Sub-Issues)
- [Task: ci.ymlのトリガー設定からmainブランチ指定を削除する](../tasks/task-remove-branch-filter-from-ci.md)

## As-is (現状)
`.github/workflows/ci.yml`には`main`ブランチを対象とする`branches`フィルタが設定されている。

## To-be (あるべき姿)
`.github/workflows/ci.yml`から`branches`フィルタが削除され、すべてのPull RequestでCIが実行される。

## 完了条件 (Acceptance Criteria)
- [ ] [Task: ci.ymlのトリガー設定からmainブランチ指定を削除する](../tasks/task-remove-branch-filter-from-ci.md)

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-011`
- **作業ブランチ (Feature Branch):** `story/update-ci-trigger-for-all-branches`
