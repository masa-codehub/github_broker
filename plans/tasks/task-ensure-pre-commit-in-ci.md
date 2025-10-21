# 目的とゴール / Purpose and Goals
# Issue: #1513
Status: Open
# 【Task】CIワークフローでpre-commitが実行されることを確認する

## 親Issue (Parent Issue)
- #1507

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
CIワークフローでpre-commitが実行されているか不明確、または設定されていない可能性がある。

## To-be (あるべき姿)
CIワークフロー(`.github/workflows/ci.yml`)内で`pre-commit run --all-files`が確実に実行され、Pull Requestに対してドキュメント検証が自動的に行われる状態になる。

## 完了条件 (Acceptance Criteria)
- [ ] `.github/workflows/ci.yml`をレビューし、`pre-commit run --all-files`または同等のコマンドが実行されるステップが存在することを確認する。
- [ ] もしステップが存在しない場合、`pre-commit`を実行するステップを追加する。
- [ ] 意図的に規約違反のドキュメントを含むPRを作成し、CIが失敗することを確認するテストを行う。

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## 影響範囲と今後の課題 / Impact and Future Issues

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-doc-validation-script`
- **作業ブランチ (Feature Branch):** `task/ensure-pre-commit-in-ci`
