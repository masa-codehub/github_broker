# 【Task】フォルダ構造チェック機能を実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## Status
- Not Created

# 目的とゴール / Purpose and Goals
設計書に定義されたフォルダ構造ルールを検証する`check_folder_structure`関数を実装し、その動作を保証する単体テストを作成する。

## As-is (現状)
フォルダ構造を検証するロジックが存在しない。

## To-be (あるべき姿)
`check_folder_structure`関数が、設計書通りのフォルダ構造違反を検出し、適切なエラーメッセージを返す。

## 手順 (Steps)
1. `scripts/validate_documents.py`に`check_folder_structure(filepath)`関数を実装する。
2. 以下のロジックを実装する:
    - `epic-*`ファイルが`plans/`直下に存在するか検証する。
    - `story-*`ファイルが`plans/*/stories/`配下に存在するか検証する。
    - `task-*`ファイルが`plans/*/tasks/`配下に存在するか検証する。
3. `tests/scripts/test_validate_documents.py`に、上記の各フォルダ構造ルールに対するテストケースを追加する。
    - 正しいフォルダ構造でエラーが返らないことを確認するテスト。
    - 不正なフォルダ構造で適切なエラーメッセージが返ることを確認するテスト。

## 完了条件 (Acceptance Criteria)
- TDDに従って実装と単体テストが完了していること。
- `check_folder_structure`関数が設計書通りの仕様で実装されていること。
- すべての単体テストがパスすること。

## 成果物 (Deliverables)
- `scripts/validate_documents.py` (更新)
- `tests/scripts/test_validate_documents.py` (更新)

## 実施内容 / Implementation
(記述不要)

## 検証結果 / Validation Results
(記述不要)

## 影響範囲と今後の課題 / Impact and Future Issues
(記述不要)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-validation-rules`
- **作業ブランチ (Feature Branch):** `task/implement-folder-structure-check`