# 【Task】`GeminiExecutor` のプロンプト構築メソッドを修正する

## 目的とゴール / Purpose and Goals
このTaskの目的は、`GeminiExecutor` がプロンプトを構築する際に、`base_branch_name` を外部から引数として受け取れるようにメソッドシグネチャを修正することです。これにより、`GeminiExecutor` の責務をプロンプト構築に限定し、データ取得ロジックから分離します。

## 実施内容 / Implementation
- `github_broker/infrastructure/executors/gemini_executor.py` の `build_prompt`（または関連するメソッド）の引数に `base_branch_name` を追加します。
- メソッド内で、受け取った `base_branch_name` を使ってプロンプトの `{base_branch_name}` 変数を置換するロジックを実装します。
- 関連するテストコードを修正し、新しい引数を渡すように変更します。

## 検証結果 / Validation Results
- `GeminiExecutor` のメソッドが `base_branch_name` を引数として受け取り、プロンプトを正しく構築できること。
- テストが成功すること。

## 影響範囲と今後の課題 / Impact and Future Issues
- 影響範囲: `GeminiExecutor` のメソッドインターフェースと、その呼び出し元。
- 今後の課題: なし。

## 親Issue (Parent Issue)
- (Story起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- `docs/design-docs/003-prompt-template-updates.md`

## 実装の参照資料 (Implementation Reference Documents)
- (なし)

## As-is (現状)
- `GeminiExecutor` のプロンプト構築メソッドが `base_branch_name` を引数として受け取らない。

## To-be (あるべき姿)
- `GeminiExecutor` のプロンプト構築メソッドが `base_branch_name` を引数として受け取り、プロンプトテンプレートの `{base_branch_name}` 変数を置換する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `github_broker/infrastructure/executors/gemini_executor.py` を開く。
2. `build_prompt`（または関連するメソッド）のシグネチャを変更し、`base_branch_name: str` を引数に追加する。
3. メソッド内で、引数で受け取った `base_branch_name` を使ってプロンプトの変数を置換する。
4. このメソッドを呼び出している箇所のコードと、関連するテストコードを修正する。

## 完了条件 (Acceptance Criteria)
- TDD（テスト駆動開発）のサイクル（Red-Green-Refactor）に従って実装と単体テストが完了していること。
- すべての単体テストがパスし、コードカバレッジが規定の基準を満たしていること。

## 成果物 (Deliverables)
- 更新された `github_broker/infrastructure/executors/gemini_executor.py`
- 更新された `tests/infrastructure/executors/test_gemini_executor.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/add-base-branch-name-variable`
- **作業ブランチ (Feature Branch):** `task/modify-gemini-executor-for-base-branch`
