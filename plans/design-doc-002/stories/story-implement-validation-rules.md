# 【Story】検証ルールを実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## Status
- Not Created

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/002-document-validator-script.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

# 目的とゴール / Purpose and Goals
設計書に定義された全ての検証ルール（命名規則、フォルダ構造、必須セクション）を実装し、単体テストによってその正しさを保証する。

## As-is (現状)
スクリプトの基本構造のみが存在し、具体的な検証ロジックは実装されていない。

## To-be (あるべき姿)
設計書`docs/design-docs/002-document-validator-script.md`に定義された全ての検証ルール（命名規則、フォルダ構造、必須セクション）が実装され、単体テストによってその正しさが保証されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: 命名規則チェック機能を実装する` を実行する。
2. `Task: フォルダ構造チェック機能を実装する` を実行する。
3. `Task: 必須セクションチェック機能を実装する` を実行する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `check_naming_convention()` が設計書通りの命名規則違反を検出できること。
- `check_folder_structure()` が設計書通りのフォルダ構造違反を検出できること。
- `check_required_sections()` が設計書通りの必須セクション欠如やタイトル不整合を検出できること。
- 各検証ルールの単体テストが全てパスすること。

## 成果物 (Deliverables)
- `scripts/validate_documents.py` (更新)
- `tests/scripts/test_validate_documents.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-document-validator`
- **作業ブランチ (Feature Branch):** `story/implement-validation-rules`