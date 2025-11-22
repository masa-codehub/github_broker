# 概要 / Summary
[ADR-018] Issue作成と検証ロジックの`issue-creator-kit`リポジトリへの分離

- Status: 提案中
- Date: 2025-11-22

## 状況 / Context

現在の`github_broker`リポジトリは、エージェントへのIssue割り当てという中核機能に加え、ドキュメントの構文検証 (`pre-commit`フック) や、`_in_box`ディレクトリを利用したIssueの自動起票など、複数の責務を担っています。

これにより、リポジトリの責務が肥大化し、単一責任の原則(SRP)に反している状態です。特に、ドキュメント検証やIssue自動起票のロジックは、CI/CDプロセスに密接に関連しており、他のリポジトリでも再利用される可能性のある汎用的な機能です。これらの機能を分離することで、`github_broker`は本来の責務に集中でき、メンテナンス性とモジュール性が向上します。

## 決定 / Decision

ドキュメント検証とIssue自動起票に関連するすべてのロジック、テスト、ドキュメントを`github_broker`リポジトリから抽出し、**`issue-creator-kit`** という名前の新しいリポジトリに分離します。

2.  **`issue-creator-kit`の内部構造 (Clean Architecture):**
    *   `issue-creator-kit`内部のPythonパッケージは、Clean Architectureの原則に基づき、以下のレイヤーに分割してリファクタリングします。この構造は、責務の分離を明確にし、将来的な拡張性を確保することを目的とします。
    *   **適用方針:** 当初はすべてのレイヤーにファイルが完全に配置される必要はありません。重要なのは、開発者がこの構造を意識し、コードが適切なレイヤーに配置されるように努めることです。

        ```
        /issue_creator_kit/
        │
        ├── issue_creator_kit/      # パッケージ本体
        │   ├── domain/             # ドメイン層: ビジネスロジックの中核 (IssueFileクラス、検証ルールなど)
        │   │   └── entities.py
        │   │
        │   ├── application/        # アプリケーション層: ユースケース (Issue作成、ファイル検証のオーケストレーション)
        │   │   └── services.py
        │   │
        │   ├── infrastructure/     # インフラ層: 外部へのアダプタ (ファイルシステム読み書き、'gh' CLI呼び出しなど)
        │   │   ├── file_system.py
        │   │   └── github_cli.py
        │   │
        │   └── interface/          # インターフェース層: エントリーポイント (CLIコマンド定義など)
        │       └── cli.py
        │
        ├── tests/
        │   ├── domain/
        │   ├── application/
        │   ├── infrastructure/
        │   └── interface/
        │
        └── pyproject.toml
        ```

    *   **Domain:** Issueファイルの属性や検証ルールなど、プロジェクト固有のビジネスロジックを定義。外部に依存しない純粋なPythonコード。
    *   **Application:** Domainのオブジェクトとルールを用いて、特定のユースケース（例: Issueファイルの検証、Issueの起票）を実現するビジネスプロセスを定義。
    *   **Infrastructure:** ファイルシステム操作、外部API（GitHub CLIなど）との連携といった、技術的な詳細を実装。Application層のインターフェースを実装する形で、依存性の逆転を適用。
    *   **Interface:** コマンドライン引数の解析やHTTPリクエストの処理など、ユーザーやシステムとの接点を定義。Application層のサービスを呼び出す。

3.  **提供するCLIコマンド:**
    *   `issue-creator-kit`は、`pyproject.toml`の`[project.scripts]`を通じて、以下のCLIコマンドを提供します。
        *   `doc-validator`: ドキュメント検証機能の呼び出し。
        *   `issue-creator`: Issue自動起票機能の呼び出し。
    *   **`pyproject.toml`設定例:**
        ```toml
        [project.scripts]
        doc-validator = "issue_creator_kit.interface.cli:validate_documents"
        issue-creator = "issue_creator_kit.interface.cli:create_issues"
        ```

4.  **`issue-creator-kit`リポジトリの構成:**
    *   このリポジトリは、`pyproject.toml`を持つインストール可能なPythonパッケージとして構成します。
    *   PyPIのような外部リポジトリには公開せず、GitHub Actionsのワークフローから`pip install git+https://...`の形式で直接インストールされることを想定します。

4.  **`issue-creator-kit`へ移行するコンポーネント:**
    *   **コアロジック (Pythonモジュール):**
        *   `github_broker/infrastructure/document_validation/` (検証、解析、フィルタリング機能)
        *   `github_broker/infrastructure/github_actions/` に含まれる全ファイル (`issue_creator.py`, `github_action_utils.py`, `github_client_for_issue_creator.py`, `main.py`)
        *   **これらのコードは、上記Clean Architectureレイヤーに合わせて再構成されます。**
    *   **テスト:**
        *   `tests/infrastructure/document_validation/`
        *   `tests/infrastructure/github_actions/` に含まれる全てのテスト (`test_issue_creator.py`, `test_github_action_utils.py`, `test_github_client_for_issue_creator.py` 等)
        *   **これらのテストは、対応するClean Architectureレイヤーのテストディレクトリに移動されます。**
    *   **ドキュメント:**
        *   `docs/architecture/adr-017-issue-creator-workflow/` のうち、`issue-creator-kit`の技術仕様として必要なドキュメント。
        *   **注記:** `docs/adr/017-commit-triggered-issue-creation.md` および `plans/adr-017/` は、`github_broker`リポジトリでの意思決定の歴史的文脈を保持するため、**移行せず、このリポジトリに残します。** ADR-017には、実装が`issue-creator-kit`に分離された旨を追記します。
    *   **依存関係の定義:**
        *   Pythonパッケージの依存関係（例: `PyYAML`、CLIインターフェース用の`click`や`typer`など）を`pyproject.toml`に定義します。
        *   システムレベルの依存関係として、GitHub CLI (`gh`) が実行環境に必要です。

5.  **`github_broker`リポジトリの変更点:**
    *   **`.github/workflows/`:**
        *   `issue_creator.yml`: 長いインラインスクリプトを削除し、`pip install git+https://github.com/<org>/issue-creator-kit.git` と、それが提供するコマンド (`issue-creator`など) の呼び出しに置き換えます。
        *   `ci.yml`: `pre-commit`フックが利用する検証コマンドのために、同様に `pip install git+https://github.com/<org>/issue-creator-kit.git` のステップを追加します。
    *   **`.pre-commit-config.yaml`:**
        *   `doc-validation`フックのエントリーポイントを、ローカルスクリプトのパスから`issue-creator-kit`が提供するコマンド (`doc-validator`など) に変更します。
    *   **アプリケーションコード (`github_broker/`):**
        *   コアなIssue割り当て機能に関するコードは変更せず、そのまま残します。

## 結果 / Consequences

### メリット (Positive consequences)

-   **責務の分離:** `github_broker`がIssue割り当て機能に専念でき、コードベースがクリーンになります。
-   **再利用性の向上:** `issue-creator-kit`は、同様のCI/CDプロセスを持つ他のリポジトリでも簡単に再利用可能になります。
-   **メンテナンス性の向上:** 各コンポーネントが自身の責務に集中しているため、個別の開発、テスト、デプロイが容易になります。

### デメリット (Negative consequences)

-   **リポジトリ管理の複雑化:** 管理すべきリポジトリが一つ増え、`issue-creator-kit`のバージョン管理が必要になります。
    -   **バージョン管理戦略:** `issue-creator-kit`はセマンティックバージョニングに従い、リリースごとにGitのタグ（例: `v1.0.0`）を付与します。`github_broker`のワークフローは、特定のブランチではなく、このGitタグを指定して`issue-creator-kit`をインストールすることにより（例: `pip install git+https://...@v1.0.0`）、依存関係を安定させ、予期せぬ変更からの影響を回避します。
-   **依存関係:** `github_broker`のCI/CDが、外部の`issue-creator-kit`リポジトリに依存するようになります。

## 検証基準 / Verification Criteria

### フェーズ1完了時の検証基準
- `github_broker`リポジトリのルートに`issue_creator_kit`ディレクトリが作成され、すべての対象コンポーネントが移動されていること。
- `github_broker/infrastructure/document_validation/`および`github_broker/infrastructure/github_actions/`が削除されていること。
- ローカルパス参照を使用した`pre-commit`フックが正常に動作すること。
- ローカルパス参照を使用した`issue_creator.yml`ワークフローが正常に動作すること。

### フェーズ2完了時の検証基準
-   `github_broker`の`pre-commit`フックが、`issue-creator-kit`をインストールした上で、ドキュメント検証を正常に実行できること。
-   `issue_creator.yml`ワークフローが、`issue-creator-kit`をインストールし、`_in_box`内のファイルからIssueを正常に自動起票できること。
-   `github_broker`のコア機能（エージェントへのIssue割り当て）が、このリファクタリングによる影響を受けないこと。
-   `issue-creator-kit`リポジトリ内のすべてのテストが、そのリポジトリのCIでパスすること。

## 実装状況 / Implementation Status
- [ ] 未着手

## 実装戦略 / Implementation Strategy

このリファクタリングは、リスクを低減するために以下の2段階のフェーズで実行します。

### フェーズ1: ローカルでのリファクタリングと集約

1.  **ローカルディレクトリの作成:** `github_broker`リポジトリのルートに`issue_creator_kit`ディレクトリを新規作成し、ADRで決定したパッケージ構造（`issue_creator_kit/pyproject.toml`, `issue_creator_kit/issue_creator_kit/`等）を構築します。
2.  **コンポーネントの移動:** ADRの「`issue-creator-kit`へ移行するコンポーネント」で特定された全てのファイルを、新しい`issue_creator_kit`ディレクトリ内に移動・再配置します。元のパスにあったファイルは`git rm`で削除し、`github_broker`内に一切関連機能が残らないようにします。
3.  **編集可能モードでのインストール:** `github_broker`の`.github/workflows/`および`.pre-commit-config.yaml`が参照するPython環境で、`pip install -e ./issue_creator_kit` を実行するようにします。
4.  **エントリーポイントの参照:** `.pre-commit-config.yaml`と`issue_creator.yml`は、ローカルパスではなく、編集可能モードでインストールされた`doc-validator`や`issue-creator`といったコマンド（エントリーポイント）を直接呼び出すように変更します。
5.  **動作確認:** この状態で、既存のCI/CDと`pre-commit`フックがすべて正常に動作することを確認します。

### フェーズ2: リポジトリの完全分離

1.  **新規リポジトリ作成:** `issue-creator-kit`という名前で新しいGitHubリポジトリを作成します。
2.  **コードの移行:** フェーズ1で作成したローカルの`issue_creator_kit`ディレクトリの内容を、新しいリポジトリにプッシュします。このリポジトリをPythonパッケージとして構成します。
3.  **参照方式の最終化:** `github_broker`側の参照を、ローカルパス参照から`pip install git+https://...`によるパッケージインストール方式に切り替えます。

#### 移行時の注意点
ワークフローのYAMLファイルには、最終的な切り替えをスムーズに行うため、一時的に古いコマンド（フェーズ1のローカルパス参照）と新しいコマンド（フェーズ2のパッケージインストール）を両方記述し、新しい方をコメントアウトしておく手法を取ります。これにより、安全なテストと簡単な切り替えが可能になります。
