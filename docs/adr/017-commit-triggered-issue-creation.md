# 概要 / Summary
[ADR-017] _in_box方式によるIssue自動起票ワークフローの導入

- Status: 承認済み
- Date: 2025-11-20

## 状況 / Context

現在、プロジェクトにはGitHubのイベントをポーリングし、Issueのライフサイクル管理やエージェントへのタスク割り当てを行う`github_broker`が存在します。`ADR-003: ポーリング方式アーキテクチャへの完全移行` および `ADR-009: ロングポーリング方式の廃止とシンプルポーリングへの切り替え` により、`github_broker`はWebhookベースのプッシュ型イベント処理から、ポーリングベースのプル型イベント処理へと完全に移行しています。

ユーザーから、コミット内容に基づいてIssueを自動起票する仕組みの要望がありました。これは、GitリポジトリをIssue作成のキューとして利用する「GitOps」的なアプローチであり、`/_in_box`フォルダに置かれたIssueファイルをトリガーとして、Issueの自動起票と処理済みファイルの移動を行うものです。この仕組みは`github_broker`に依存せず汎用的な形で実装し、また、既存のCIワークフローとは分離して動作させる必要があります。

Issueファイルのフォーマット検証については、既存の`pre-commit`フックの機能を`plans/`フォルダから`/_in_box`フォルダの監視に転用することで再利用します。また、Issue化に失敗したファイルを追跡するため、`/_failed_box`フォルダを導入します。

なお、今回の決定に伴い、既存のGitHubのWeb UIからのIssue作成をガイドする`.github/ISSUE_TEMPLATE`および、Issue作成後の自動検証を行う`.github/workflows/issue_validator.yml`は**廃止**し、これらを削除します。これは、`/_in_box`方式がIssue作成の唯一の手段となるため、これら既存の仕組みによる品質チェックは不要と判断されたためです。

## 決定 / Decision

Issue自動起票の機能は、**GitHub Actions Workflow** として`.github/workflows/` ディレクトリに実装します。このワークフローは、特定のPull Requestが`main`ブランチにマージされた時にのみトリガーされます。

この決定は、`/_in_box`方式がIssue作成の唯一の手段となることを意味します。これに伴い、既存の`.github/ISSUE_TEMPLATE`および`.github/workflows/issue_validator.yml`によるIssue作成のガイドおよび自動検証メカニズムは削除されます。

**ワークフローの詳細:**

1.  **トリガー:** Pull Requestが`main`ブランチにマージされた時（`on: pull_request: types: [closed], branches: [main]` かつ `if: github.event.pull_request.merged == true`）。
2.  **対象ファイル:** マージされたPull Requestに含まれる`/_in_box/`フォルダ内のファイル（Issueファイル）を処理対象とします。
3.  **Issueファイルのフォーマット:** 既存の`pre-commit`フック（`doc-validation`）の設定を更新し、`/_in_box/`フォルダ内のファイルを確実にチェックするようにします。これにより、Pull Requestが`main`ブランチにマージされる前に、Issueファイルのフォーマット（例: YAML Front Matterによるメタデータ定義とMarkdown本文）の妥当性が保証されます。
4.  **CIとの連携:** `/_in_box/`フォルダ内のファイルがPull Requestの時点で確実に検証されるよう、CIワークフロー (`.github/workflows/ci.yml`) はドキュメントファイル (`.md`) の変更を無視しないように設定されます。これにより、`pre-commit`フックがすべてのドキュメント変更に対して実行されることが保証されます。
5.  **Issue作成ロジック:**
    *   各Issueファイルの内容を読み込み、Issueのタイトル、本文、ラベル、担当者などの情報を抽出します。
    *   `gh cli` または `actions/github-script` を使用してGitHub Issueを作成します。
6.  **ファイル移動とコミット:**
    *   Issueの作成が成功したファイルは`/_in_box/`から`/_done_box/`に移動します。
    *   Issueの作成に失敗したファイルは`/_in_box/`から`/_failed_box/`に移動します。
    *   ファイル移動の変更は、新しいコミットとして`main`ブランチにプッシュされます。このコミットは`on: pull_request`をトリガーとする当ワークフローを再トリガーしないため、無限ループの心配はありません。
7.  **ワークフローの分離:**
    *   このIssue起票ワークフローは、既存のCIワークフロー（`pull_request`イベント時に`pre-commit`を実行）とは**独立した別のワークフローファイル**として定義されます。これにより、責務が分離され、CIが通った品質保証済みのファイルのみがIssue起票の対象となります。

## 結果 / Consequences

### メリット (Positive consequences)

- **汎用性と再利用性:** プロジェクト固有の`github_broker`に依存せず、GitHubのネイティブ機能で実装されるため、他のGitHubリポジトリにも容易に適用可能となり、汎用性が大幅に向上します。
- **既存アーキテクチャとの非干渉:** `github_broker`の既存のポーリングベースのアーキテクチャに影響を与えることなく、新しい機能を追加できます。
- **無限ループのリスクの抜本的解消:** Pull Requestマージをトリガーとすることで、自動コミットがワークフローを再トリガーする無限ループの問題を安全に回避できます。
- **堅牢な開発プロセス:**
    *   `pre-commit`フックによるIssueファイルの事前検証を強制することで、品質の高いIssueファイルのみが`main`にマージされ、Issue起票の信頼性が向上します。
    *   `/_done_box`と`/_failed_box`の導入により、処理の成功・失敗が明確になり、運用上の追跡が容易になります。
- **メンテナンス性:** GitHubのネイティブ機能として提供されるため、メンテナンスが容易であり、GitHub Actionsのエコシステムを活用できます。
- **セキュリティ:** GitHub Actionsの標準的な認証・認可メカニズムにより、セキュアに運用できます。

### デメリット (Negative consequences)

- **ロジックの管理:** Issue本文の生成やファイル移動ロジックはGitHub ActionsのYAMLまたはスクリプト内に記述されるため、複雑なロジックは適切な設計とコメントが必要となります。ただし、テンプレート化と分離により、管理は容易になります。

## 検証基準 / Verification Criteria

-   `/_in_box/`フォルダにIssueファイルを加えるPull Requestが`main`にマージされた際、GitHubリポジトリに新しいIssueが自動的に作成されること。
-   作成されたIssueのタイトル、本文、ラベル、担当者などが、Issueファイルの内容に基づいて適切に生成されていること。
-   Issue作成後、処理されたIssueファイルが`/_in_box/`から`/_done_box/`に移動し、その変更が`main`ブランチに自動コミットされていること。
-   Issue作成に失敗した場合、対象のIssueファイルが`/_in_box/`から`/_failed_box/`に移動し、その変更が`main`ブランチに自動コミットされていること。
-   ワークフローの実行ログにおいて、エラーなくIssueが作成され、ファイル移動が完了したことが確認できること。

## 実装状況 / Implementation Status

- [x] 完了

**追記 (2025-11-25):**
本ADRで決定されたワークフローは、`ADR-018: Issue作成と検証ロジックの関心事を分離する` に基づき、`issue_creator_kit`パッケージとしてリファクタリングされました。Issue作成のロジックは現在、GitHub ActionsのWorkflow内ではなく、この独立したパッケージに内包されています。
