# 【Epic】すべてのブランチへのPull RequestでCIをトリガーする

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- [Story: CIワークフローが全ブランチへのPRでトリガーされるようにする](stories/story-update-ci-trigger.md)

## As-is (現状)
CIワークフローは`main`ブランチに対するPull Requestでのみ実行される。

## To-be (あるべき姿)
CIワークフローが、すべてのブランチを対象とするPull Requestで実行されるようになる。

## 完了条件 (Acceptance Criteria)
- [ ] Story: CIワークフローが全ブランチへのPRでトリガーされるようにする

## 成果物 (Deliverables)
- `.github/workflows/ci.yml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-011`
