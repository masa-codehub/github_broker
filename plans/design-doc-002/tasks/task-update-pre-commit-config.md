# 【Task】pre-commitフックを設定ファイルに統合する

## 親Issue (Parent Issue)
- (起票後に追記)

## Status
- Not Created

# 目的とゴール / Purpose and Goals
完成した検証スクリプトを、`.pre-commit-config.yaml`にフックとして追加し、コミット時に自動実行されるようにする。

## As-is (現状)
検証スクリプトが`pre-commit`に統合されていない。

## To-be (あるべき姿)
`.pre-commit-config.yaml`に`document-validator`フックが追加され、コミット時に自動で検証が実行される。

## 手順 (Steps)
1. `.pre-commit-config.yaml`を開く。
2. 設計書`docs/design-docs/002-document-validator-script.md`の「3.5. pre-commitへの統合方法」セクションを参考に、`document-validator`フックの定義を追加する。
3. `entry`が`python scripts/validate_documents.py`を指していることを確認する。
4. `files`の正規表現が、対象となる全てのドキュメント（ADR, Design Doc, plans）を正しく捕捉することを確認する。

## 完了条件 (Acceptance Criteria)
- `.pre-commit-config.yaml`に`document-validator`フックが正しく追加されていること。
- `pre-commit run document-validator --all-files` を実行した際に、スクリプトが実行されること。

## 成果物 (Deliverables)
- `.pre-commit-config.yaml` (更新)

## 実施内容 / Implementation
(記述不要)

## 検証結果 / Validation Results
(記述不要)

## 影響範囲と今後の課題 / Impact and Future Issues
(記述不要)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/integrate-with-pre-commit`
- **作業ブランチ (Feature Branch):** `task/update-pre-commit-config`