# 【Story】pre-commitフックへ統合する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (起票後に追記)

## Status
- Not Created

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/002-document-validator-script.md`

## 実装の参照資料 (Implementation Reference Documents)
- `.pre-commit-config.yaml`

# 目的とゴール / Purpose and Goals
完成した検証スクリプトを`.pre-commit-config.yaml`にフックとして登録し、`git commit`時に指定されたMarkdownファイルに対して自動的に実行されるようにする。

## As-is (現状)
検証スクリプトは存在するが、開発ワークフローには統合されておらず、手動で実行する必要がある。

## To-be (あるべき姿)
検証スクリプトが`.pre-commit-config.yaml`にフックとして登録され、`git commit`時に指定されたMarkdownファイルに対して自動的に実行される。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: pre-commitフックを設定ファイルに統合する` を実行する。
2. `Task: pre-commitフックの統合テストを作成する` を実行する。

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- `.pre-commit-config.yaml`に、設計書通りの設定で`document-validator`フックが追加されていること。
- 規約に準拠したファイルを変更した場合は、コミットが成功すること。
- 規約違反のファイルを変更した場合は、コミットが失敗し、スクリプトから適切なエラーメッセージが出力されること。
- 統合テストがパスすること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml` (更新)
- `tests/integration/test_pre_commit_validator.py` (新規作成)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-document-validator`
- **作業ブランチ (Feature Branch):** `story/integrate-with-pre-commit`
