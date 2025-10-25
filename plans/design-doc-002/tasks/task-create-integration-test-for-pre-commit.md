# 【Task】pre-commitフックの統合テストを作成する

## 親Issue (Parent Issue)
- (起票後に追記)

## Status
- Not Created

# 目的とゴール / Purpose and Goals
`pre-commit`フックとして統合された検証スクリプトが、実際のコミットワークフローで意図通りに動作することを確認するための統合テストを作成する。

## As-is (現状)
`pre-commit`フックの動作を保証する自動テストが存在しない。

## To-be (あるべき姿)
`pre-commit`フックが、規約違反のコミットを正しくブロックし、規約準拠のコミットを許可することを自動で検証できる。

## 手順 (Steps)
1. テスト用のディレクトリ（例: `tests/integration/pre_commit_validator`）を作成する。
2. 規約に準拠したMarkdownファイルのサンプルを作成する。
3. 規約違反のMarkdownファイルのサンプルを複数作成する（命名規則違反、フォルダ構造違反、必須セクション違反など）。
4. 上記サンプルファイルを使って、`pre-commit run`コマンドが期待通りに成功または失敗するかを検証するテストスクリプトを作成する。
    - 正常なファイルのみをステージングした場合は、コミット（または`pre-commit run`）が成功することを確認する。
    - 違反ファイルを含む場合は、コミット（または`pre-commit run`）が失敗し、適切なエラーメッセージが出力されることを確認する。

## 完了条件 (Acceptance Criteria)
- TDDに従って実装と統合テストが完了していること。
- `pre-commit`フックの動作を検証する自動テストが作成されていること。
- すべての統合テストがパスすること。

## 成果物 (Deliverables)
- `tests/integration/test_pre_commit_validator.py` (新規作成)
- テスト用のサンプルMarkdownファイル

## 実施内容 / Implementation
(記述不要)

## 検証結果 / Validation Results
(記述不要)

## 影響範囲と今後の課題 / Impact and Future Issues
(記述不要)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-with-pre-commit`
- **作業ブランチ (Feature Branch):** `task/create-integration-test-for-pre-commit`
