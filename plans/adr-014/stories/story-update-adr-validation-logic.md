# 【Story】ADR検証ロジックを更新する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

# 目的とゴール / Purpose and Goals
`scripts/validate_docs.py`にADRの新しい検証ルールを実装し、ADRの品質と一貫性を向上させる。

## As-is (現状)
`scripts/validate_docs.py`はADRに対して基本的なセクションチェックしか行っておらず、正規表現による検証は行われていない。

## To-be (あるべき姿)
`scripts/validate_docs.py`がADRの必須セクションと概要の正規表現を検証し、規約に準拠しないADRを検出できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: scripts/validate_docs.py`にADRの必須セクション検証ロジックを追加する。
2. `Task: scripts/validate_docs.py`にADRの概要正規表現検証ロジックを追加する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- 新しいADR検証ルールが`scripts/validate_docs.py`に正しく実装されていること。

## 成果物 (Deliverables)
- `scripts/validate_docs.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-014`
- **作業ブランチ (Feature Branch):** `story/update-adr-validation-logic`
