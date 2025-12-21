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
