# 目的とゴール / Purpose and Goals
# Issue: #1518
Status: Open
# 【Task】ci.ymlのトリガー設定からmainブランチ指定を削除する

## 親Issue (Parent Issue)
- #1517

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
`.github/workflows/ci.yml`は以下のように設定されている。
```yaml
on:
  pull_request:
    branches:
      - main
```

## To-be (あるべき姿)
`.github/workflows/ci.yml`の`on.pull_request`設定から`branches`フィルタが削除され、CIコストを最適化するための設定が追加される。
```yaml
on:
  pull_request:
    types:
      - opened
      - synchronize
      - reopened
      - ready_for_review
    paths-ignore:
      - 'docs/**'
      - 'plans/**'
      - '**.md'
```

## 完了条件 (Acceptance Criteria)
- [ ] `.github/workflows/ci.yml`の`on.pull_request`セクションが`branches`キーを持たない状態になっていること。
- [ ] `main`以外のブランチへのPull RequestでCIワークフローが正常に実行されることを確認する。
- [ ] `main`ブランチへのPull RequestでもCIが実行されること。
- [ ] ドキュメントのみの変更を含むPull RequestではCIがスキップされること。

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## 影響範囲と今後の課題 / Impact and Future Issues

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/update-ci-trigger-for-all-branches`
- **作業ブランチ (Feature Branch):** `task/remove-main-branch-filter-from-ci`
