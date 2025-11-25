# 【Task】検証サービスの作成

## 親Issue (Parent Issue)
- `story-implement-validation-logic` (起票後にIssue番号を記載)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/019-fix-issue-creator-workflow.md`

## As-is (現状)
`issue_creator_kit/application/`配下に、フロントマターを検証するサービスが存在しない。

## To-be (あるべき姿)
`issue_creator_kit/application/validation_service.py`が作成され、ADR-019の検証ロジック（フロントマターの存在確認、titleフィールドの検証、labels/related_issuesの型検証）を実装した`validate_frontmatter`関数が定義されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `issue_creator_kit/application/validation_service.py`ファイルを作成する。
2. `validate_frontmatter`関数を実装する。この関数はファイルパスを引数に取り、内部でファイルを読み込み、フロントマターをパースして検証を行う。
3. ADR-019で定義された検証ルールに違反した場合は、具体的なエラーメッセージと共に例外を送出する。

## 完了条件 (Acceptance Criteria)
- TDDのサイクルに従い、対応する単体テスト(`test_validation_service.py`での実装)がパスする`validate_frontmatter`関数が実装されていること。

## 成果物 (Deliverables)
- `issue_creator_kit/application/validation_service.py`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/implement-validation-logic`
- **作業ブランチ (Feature Branch):** `task/create-validation-service`
