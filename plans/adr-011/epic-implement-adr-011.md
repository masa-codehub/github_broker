# 目的とゴール / Purpose and Goals
# Issue: #1516
Status: Open
# 【Epic】すべてのブランチへのPull RequestでCIをトリガーする

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- #1517

## As-is (現状)
CIワークフローは`main`ブランチに対するPull Requestでのみ実行される。

## To-be (あるべき姿)
CIワークフローが、すべてのブランチを対象とするPull Requestで実行されるようになる。

## 完了条件 (Acceptance Criteria)
- [ ] Story: CIワークフローが全ブランチへのPRでトリガーされるようにする

## 実施内容 / Implementation

## 検証結果 / Validation Results

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## 影響範囲と今後の課題 / Impact and Future Issues

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-011`
