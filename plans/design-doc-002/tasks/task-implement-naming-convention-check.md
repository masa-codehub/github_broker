# 【Task】命名規則チェック機能を実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## Status
- Not Created

# 目的とゴール / Purpose and Goals
設計書に定義されたファイル命名規則を検証する`check_naming_convention`関数を実装し、その動作を保証する単体テストを作成する。

## As-is (現状)
命名規則を検証するロジックが存在しない。

## To-be (あるべき姿)
`check_naming_convention`関数が、設計書通りの命名規則違反を検出し、適切なエラーメッセージを返す。

## 手順 (Steps)
1. `scripts/validate_documents.py`に`check_naming_convention(filepath)`関数を実装する。
2. 以下のロジックを実装する:
    - `plans/`配下のファイル名が`epic-`, `story-`, `task-`で始まるか検証する。
    - `docs/adr/`配下のファイル名が`[ADR-XXX]`で始まるか検証する。
    - `docs/design-docs/`配下のファイル名が`[Design Doc XXX]`で始まるか検証する。
3. `tests/scripts/test_validate_documents.py`に、上記の各命名規則に対するテストケースを追加する。
    - 正常なファイル名でエラーが返らないことを確認するテスト。
    - 不正なファイル名で適切なエラーメッセージが返ることを確認するテスト。

## 完了条件 (Acceptance Criteria)
- TDDに従って実装と単体テストが完了していること。
- `check_naming_convention`関数が設計書通りの仕様で実装されていること。
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
- **作業ブランチ (Feature Branch):** `task/implement-naming-convention-check`