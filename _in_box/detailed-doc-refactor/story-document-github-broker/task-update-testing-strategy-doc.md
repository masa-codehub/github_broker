---
title: "【Task】`TESTING_STRATEGY.md`を現在の実装とCI構成に同期"
labels: ["task", "documentation", "refactoring", "P2", "TECHNICAL_DESIGNER"]
---
# 【Task】`TESTING_STRATEGY.md`を現在の実装とCI構成に同期

## 親Issue (Parent Issue)
- (Story: `github_broker`ドキュメントの整備)

## 子Issue (Sub-Issues)
- (なし)

## 参照元の意思決定 (Source Decision Document)
- (なし)

## As-is (現状)
- `docs/guides/TESTING_STRATEGY.md`の内容が、現状の実装とCI/CDの構成と乖離している。
  - **CI戦略の不一致:** ドキュメントでは`pytest`マーカーによるテスト選択が記述されているが、`ci.yml`では常に全テストが実行されている。
  - **網羅性の欠如:** `issue_creator_kit`のテスト構成について全く言及されていない。
  - **具体性の不足:** 開発者がローカルでテストを実行するための具体的なコマンド例が記載されていない。

## To-be (あるべき姿)
- `TESTING_STRATEGY.md`が、`ci.yml`の動作（`pre-commit`経由での全テスト実行）と完全に一致した内容になる。
- `github_broker`と`issue_creator_kit`の両方のテスト構成について言及し、プロジェクト全体のテスト戦略を網羅する。
- 開発者がテストを実行・追加する際に必要となる具体的なコマンド例やディレクトリ構成ルールが明記される。

## ユーザーの意図と背景の明確化
- ユーザーは、テストという品質保証の根幹をなす活動について、開発者全員が同じ理解と手順で臨むことを求めている。ドキュメントを現状と一致させることで、テストの実行漏れを防ぎ、新規開発者がスムーズにテストコードを追加できる環境を整えることを意図している。

## **具体的な修正内容**
- **対象ファイル:** `docs/guides/TESTING_STRATEGY.md`
- **修正方法:** ファイル全体を以下の内容で**上書き**する。

```markdown
# テスト戦略ガイドライン

## 1. 全体方針

本プロジェクトでは、品質と開発速度を両立させるため、**テストピラミッド**の考え方を採用します。テストは自動化され、CI/CDパイプラインに組み込まれることを前提とします。

- **テストフレームワーク:** `pytest` を標準とします。
- **CIでの実行:** CIでは`pre-commit`フックを通じて、常に**全てのテスト**が実行されます。

## 2. ディレクトリ構成と命名規則

テストコードは、テスト対象のソースコードのディレクトリ構造をミラーリングします。

- **`github_broker/`のテスト:**
  - `tests/` ディレクトリ配下に配置します。
  - 例: `github_broker/application/task_service.py` のテストは `tests/application/test_task_service.py` に記述します。
- **`issue_creator_kit/`のテスト:**
  - `issue_creator_kit/tests/` ディレクトリ配下に配置します。
  - 例: `issue_creator_kit/application/issue_service.py` のテストは `issue_creator_kit/tests/application/test_issue_service.py` に記述します。

**命名規則:**
- **ファイル名:** `test_*.py` の形式
- **関数名:** `test_*` の形式で、テストする振る舞いが明確にわかるように命名します。

## 3. レイヤー毎のテスト方針

本プロジェクトはクリーンアーキテクチャを採用しており、各レイヤーの責務に応じてテストを実装します。

### 3.1. Domain Layer
- **種類:** 単体テスト
- **方針:** フレームワークや外部ライブラリに依存しない、コアなビジネスロジックをテストします。モックは原則不要です。

### 3.2. Application Layer
- **種類:** 単体テスト
- **方針:** ユースケースのフローをテストします。Infrastructure層の依存コンポーネント（`GitHubClient`, `RedisClient`等）は、`unittest.mock`を使用して**すべてモック**します。

### 3.3. Interface Layer
- **種類:** 単体テスト
- **方針:** APIエンドポイントやCLIの挙動をテストします。
    - **API (`github_broker`):** FastAPIの`TestClient`を使用し、Application層のサービスはモックします。リクエストに応じて適切なレスポンスとステータスコードが返ることを確認します。
    - **CLI (`issue_creator_kit`):** `click.testing.CliRunner` を使用し、Application層のサービスはモックします。引数に応じて適切な出力や関数の呼び出しが行われることを確認します。

### 3.4. Infrastructure Layer
- **種類:** 単体テスト と 統合テスト
- **方針:**
    - **単体テスト:** 外部ライブラリ（`PyGithub`, `redis-py`等）をモックし、クライアントクラスの内部ロジックが正しいことを検証します。
    - **統合テスト:** （限定的に）実際に外部サービスと通信し、連携が正しく機能することを確認します。これらのテストは `@pytest.mark.integration` マーカーを付与し、通常はスキップされるように設定することも検討します（現状は全実行）。

## 4. ローカルでのテスト実行

開発者は、コードの変更後にローカルでテストを実行することが推奨されます。

### 統合的な品質チェック（推奨）

CIで実行される内容と等価なチェックを、以下のコマンドで実行できます。

```bash
pre-commit run --all-files
```

### 特定のテストのみを実行

`pytest`コマンドを直接使用して、特定のテストのみを実行することも可能です。

```bash
# github_brokerの全テストを実行
pytest tests/

# issue_creator_kitの全テストを実行
pytest issue_creator_kit/tests/

# 特定のファイルのみテストを実行
pytest tests/application/test_task_service.py

# 特定のテスト関数のみ実行
pytest tests/application/test_task_service.py::test_request_task_returns_none
```

### カバレッジの計測

テストカバレッジを計測し、レポートを生成します。

```bash
pytest --cov=github_broker --cov=issue_creator_kit
```
```

## 完了条件 (Acceptance Criteria)
- `docs/guides/TESTING_STRATEGY.md` が、上記の「具体的な修正内容」で上書きされていること。

## 成果物 (Deliverables)
- 更新された `docs/guides/TESTING_STRATEGY.md`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/document-github-broker`
- **作業ブランチ (Feature Branch):** `task/update-testing-strategy-doc`
