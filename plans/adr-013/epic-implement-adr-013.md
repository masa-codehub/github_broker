# 【Epic】ADR-013: エージェント役割定義の外部設定化を実装する

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

## 実装の参照資料 (Implementation Reference Documents)
- `github_broker/application/task_service.py`
- `github_broker/infrastructure/config.py`

# 目的とゴール / Purpose and Goals
ハードコードされたエージェントの役割定義を外部のYAMLファイルで管理できるように変更することで、柔軟性とメンテナンス性を向上させる。

## As-is (現状)
エージェントの役割（Role）が `task_service.py` にハードコードされている。

## To-be (あるべき姿)
エージェントの役割定義が外部のYAMLファイルで管理され、アプリケーションは起動時にその設定を読み込んで利用する。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Story: YAMLベースのエージェント設定機構を導入する` を行い、設定ファイルの読み込みと検証の基盤を構築する。
2. `Story: TaskServiceが外部設定を利用できるようにする` を行い、アプリケーションのコアロジックを新しい設定機構に適応させる。
3. `Story: 新しい設定に対応したドキュメントを更新する` を行い、変更内容を開発者向けにドキュメント化する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、関連する意思決定ドキュメント（ADR-013）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- 更新されたソースコード
- 更新されたドキュメント

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-013`