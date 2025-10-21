# 目的とゴール
# Issue: #1517
Status: Open
# 目的とゴール / Purpose and Goals

## 親Issue (Parent Issue)
- #1516

## 子Issue (Sub-Issues)
- #1518

## As-is (現状)
`.github/workflows/ci.yml`には`main`ブランチを対象とする`branches`フィルタが設定されている。

## To-be (あるべき姿)
`.github/workflows/ci.yml`から`branches`フィルタが削除され、すべてのPull RequestでCIが実行される。

## 完了条件 (Acceptance Criteria)
- [ ] [Task: ci.ymlのトリガー設定からmainブランチ指定を削除する](../tasks/task-remove-branch-filter-from-ci.md)

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## 影響範囲と今後の課題 / Impact and Future Issues

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-011`
- **作業ブランチ (Feature Branch):** `story/update-ci-trigger-for-all-branches`
