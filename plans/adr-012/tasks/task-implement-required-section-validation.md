# 【Task】必須セクションの検証ロジックを実装する

## 親Issue (Parent Issue)
- (起票後に追記)

## 子Issue (Sub-Issues)
- (なし)

## As-is (現状)
検証ロジックが存在しない。

## To-be (あるべき姿)
対象となる全ドキュメント（ADR, Design Docs, plans）に、それぞれの種類に応じた必須セクション（Markdownヘッダー）が含まれているかを検証するPython関数が実装される。

## 完了条件 (Acceptance Criteria)
- [ ] Markdownファイルを読み込み、ヘッダー（`##`で始まる行）を抽出する関数が実装されていること。
- [ ] ドキュメントタイプごとに必須ヘッダーのリストを定義していること。
- [ ] ファイルの内容に必須ヘッダーがすべて含まれているか検証する関数が実装されていること。

## 成果物 (Deliverables)
- Python検証スクリプトの一部

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/create-doc-validation-script`
- **作業ブランチ (Feature Branch):** `task/implement-doc-content-validation`
