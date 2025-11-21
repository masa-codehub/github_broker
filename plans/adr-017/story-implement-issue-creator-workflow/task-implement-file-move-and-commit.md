# 【Task】ファイル移動と自動コミットロジックの実装

## 親Issue (Parent Issue)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/017-commit-triggered-issue-creation.md`

## 実装の参照資料 (Implementation Reference Documents)
- `docs/architecture/adr-017-issue-creator-workflow/index.md`

## As-is (現状)
ワークフローは`/_in_box/`内のファイルからIssueを作成するが、処理後のファイルをリポジトリ内で移動・管理するステップが実装されていない。

## To-be (あるべき姿)
ADR-017の`決定`事項に基づき、Issue作成の成功・失敗に応じて、処理されたファイルがそれぞれ`/_done_box/`または`/_failed_box/`に移動され、その変更が`[github-actions]`ボットによって`main`ブランチにコミットおよびプッシュされるロジックが実装されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1.  Issue作成ステップの結果（成否）を条件に、後続のステップを実行するよう設定する。
2.  Issue作成が成功した場合に`git mv "_in_box/FILENAME" "_done_box/FILENAME"`を実行するステップを追加する。
3.  Issue作成が失敗した場合に`git mv "_in_box/FILENAME" "_failed_box/FILENAME"`を実行するステップを追加する。
4.  コミットを行う前に、`git config`コマンドを使用してコミットユーザーの名前（例: `github-actions[bot]`）とメールアドレスを設定する。
5.  `git commit`コマンドを使用して、ファイル移動を記録するコミットを作成する。コミットメッセージは処理内容がわかるように（例: `chore(actions): Process issue file FILENAME`）設定する。
6.  `git push`コマンドを使用して、作成したコミットを`main`ブランチにプッシュする。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。
- ワークフロー完了後、処理されたファイルが`/_in_box`から適切なフォルダ（`_done_box` or `_failed_box`）に移動され、その変更が`main`ブランチにコミットされていること。

## 成果物 (Deliverables)
- `.github/workflows/issue-creator.yml` (最終版)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-issue-creator-workflow`
- **作業ブランチ (Feature Branch):** `task/implement-file-move-and-commit`

## 子Issue (Sub-Issues)

- 
