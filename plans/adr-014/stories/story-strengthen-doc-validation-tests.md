# 【Story】ドキュメント検証スクリプトのテストを強化する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

# 目的とゴール / Purpose and Goals
`scripts/validate_docs.py`のテストを強化し、新しい検証ルールが正しく機能することを保証する。

## As-is (現状)
`scripts/validate_docs.py`のテストは、新しい検証ルールに対応していない。

## To-be (あるべき姿)
`scripts/validate_docs.py`のテストが更新され、ADRおよびDesign Docの新しい検証ルールが正しく機能することを網羅的に検証できるようになっている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: scripts/validate_docs.py`のテストにADRの新しい検証ケースを追加する。
2. `Task: scripts/validate_docs.py`のテストにDesign Docの新しい検証ケースを追加する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- 新しい検証ルールに対するテストが網羅的に書かれていること。

## 成果物 (Deliverables)
- `tests/scripts/test_validate_docs.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-014`
- **作業ブランチ (Feature Branch):** `story/strengthen-doc-validation-tests`
