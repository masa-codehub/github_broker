# 【Task】必須セクションチェック機能を実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## Status
- Not Created

# 目的とゴール / Purpose and Goals
設計書に定義された必須セクションとタイトル整合性を検証する`check_required_sections`関数を実装し、その動作を保証する単体テストを作成する。

## As-is (現状)
必須セクションを検証するロジックが存在しない。

## To-be (あるべき姿)
`check_required_sections`関数が、設計書通りの必須セクション欠如やタイトル不整合を検出し、適切なエラーメッセージを返す。

## 手順 (Steps)
1. `scripts/validate_documents.py`に`check_required_sections(filepath)`関数を実装する。
2. ドキュメントタイプ（ADR, Design Doc, Epic, Story, Task）ごとに必須セクションのリストを定義する。
3. ファイルの内容を読み込み、コードブロック内を無視しつつ、必須セクション（Markdownヘッダー）が全て存在するか検証するロジックを実装する。
4. ADRとDesign Docに対して、ファイル名とタイトルヘッダー内の番号が一致するか、タイトルが空でないかを検証する「タイトル整合性チェック」を実装する。
5. `tests/scripts/test_validate_documents.py`に、上記の各ルールに対するテストケースを追加する。
    - 必須セクションが全て存在する正常なファイルでエラーが返らないことを確認するテスト。
    - 必須セクションが欠けている場合に適切なエラーメッセージが返ることを確認するテスト。
    - タイトル整合性チェックが正常に機能することを確認するテスト。

## 完了条件 (Acceptance Criteria)
- TDDに従って実装と単体テストが完了していること。
- `check_required_sections`関数が設計書通りの仕様で実装されていること。
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
- **作業ブランチ (Feature Branch):** `task/implement-required-sections-check`