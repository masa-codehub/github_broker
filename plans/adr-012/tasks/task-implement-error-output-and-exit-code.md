# 【Task】検証エラー時の詳細な出力と終了コードを実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
検証ロジックが成功/失敗を返すだけで、詳細なフィードバックがない。

## To-be (あるべき姿)
検証スクリプトが規約違反を検知した際に、どのファイルのどのルールに違反したかを具体的に標準エラー出力に表示し、非ゼロの終了コードで終了するCLI（Command Line Interface）が実装される。

## 完了条件 (Acceptance Criteria)
- [ ] 検証関数が違反の詳細（ファイルパス、違反内容）を返すようになっていること。
- [ ] スクリプトのメイン関数が、すべての検証を実行し、違反があった場合にエラーメッセージを整形して`sys.stderr`に出力すること。
- [ ] 違反があった場合に`sys.exit(1)`などで終了コードを1に設定すること。
- [ ] 違反がなかった場合は何も出力せず、終了コード0で正常終了すること。

## 成果物 (Deliverables)
- Python検証スクリプトのCLI部分

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-doc-validation-script`
- **作業ブランチ (Feature Branch):** `task/implement-validation-cli`
