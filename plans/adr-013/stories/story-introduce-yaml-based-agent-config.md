# 【Story】YAMLベースのエージェント設定機構を導入する

## 親Issue (Parent Issue)
- (Epic起票後に追記)

## 子Issue (Sub-Issues)
- (Task起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/013-agent-role-configuration.md`

# 目的とゴール / Purpose and Goals
エージェントの役割定義を外部YAMLファイルから読み込み、検証する基盤を構築する。

## As-is (現状)
エージェントの役割定義がPythonのクラス変数としてコード内に静的に定義されている。

## To-be (あるべき姿)
YAMLファイルに定義されたエージェント設定を読み込み、Pydanticモデルで検証し、アプリケーション内で利用できるデータ構造に変換する仕組みが構築されている。

## 目標達成までの手順 (Steps to Achieve Goal)
1. `Task: agents.ymlのサンプルファイルを作成する`
2. `Task: config.pyにAGENT_CONFIG_PATH設定を追加する`
3. `Task: YAMLファイルを読み込み検証するAgentConfigLoaderコンポーネントを作成する`
4. `Task: AgentConfigLoaderの単体テストを作成する`

## 完了条件 (Acceptance Criteria)
- このStoryを構成する全てのTaskの実装が完了していること。
- Storyに与えられた目標（To-be）が、統合テストによって達成されていることが確認されること。
- 指定されたYAMLファイルを正しく読み込めること。
- 不正な形式のYAMLファイルや存在しないパスを指定した場合に、適切にエラーを発生させること。

## 成果物 (Deliverables)
- `agents.yml.sample`
- `github_broker/infrastructure/config.py` (更新)
- `github_broker/infrastructure/agent/loader.py` (新規)
- `tests/infrastructure/agent/test_loader.py` (新規)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `epic/implement-adr-013`
- **作業ブランチ (Feature Branch):** `story/introduce-yaml-based-agent-config`