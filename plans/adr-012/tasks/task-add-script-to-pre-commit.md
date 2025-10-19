# 【Task】検証スクリプトをpre-commitフックに追加する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
`.pre-commit-config.yaml`にドキュメント検証フックが存在しない。

## To-be (あるべき姿)
`.pre-commit-config.yaml`に新しいローカルフックが追加され、コミット時にドキュメント検証スクリプトが自動実行されるようになる。

## 完了条件 (Acceptance Criteria)
- [ ] `.pre-commit-config.yaml`に、作成したPython検証スクリプトを実行するための新しい`repo: local`フックが定義されていること。
- [ ] `pre-commit run --all-files`を実行し、意図的に追加した規約違反ファイルに対してフックが失敗し、エラーメッセージが出力されること。
- [ ] 規約違反がない状態ではフックが成功すること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-doc-validation-script`
- **作業ブランチ (Feature Branch):** `task/add-doc-validation-to-pre-commit`
