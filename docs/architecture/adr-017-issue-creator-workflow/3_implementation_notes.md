# 3. 実装上の考慮事項 (Implementation Notes)

本ドキュメントは、[ADR-017] Commit-triggered Issue Creation ワークフローの実装における技術的な詳細と考慮事項をまとめたものです。

## 1. ワークフローのトリガーと実行条件

*   **トリガー:** Pull Request が `main` ブランチにマージされた時。
    *   `on: pull_request: types: [closed], branches: [main]`
    *   `if: github.event.pull_request.merged == true`
*   **対象ファイル:** マージされた Pull Request に含まれる `/_in_box/` フォルダ内のファイル（Issueファイル）のみが処理対象となります。

## 2. Issueファイルフォーマットの検証

*   **事前検証:** Issueファイル（Markdown形式、YAML Front Matterを含む）のフォーマットは、`pre-commit` フックにより Pull Request 作成時に検証されます。
*   **CIとの連携:** `ci.yml` ワークフローは、`.md` ファイルの変更を無視しないように設定され、`pre-commit` フックがすべてのドキュメント変更に対して実行されることを保証します。これにより、フォーマットが不正なファイルは `main` ブランチにマージされる前に検出されます。

## 3. Issue作成ロジック

*   **ツールの選択:** GitHub Issue の作成には、`gh cli` または `actions/github-script` を使用します。
    *   `gh cli` を使用する場合: `gh issue create --title "..." --body "..." --label "..." --assignee "..."` の形式でコマンドを実行します。
    *   `actions/github-script` を使用する場合: JavaScript を用いて GitHub API を直接操作します。Issueファイルから抽出したメタデータに基づき `github.rest.issues.create()` メソッドを呼び出します。
*   **メタデータ抽出:** Issueファイル（Markdown with YAML Front Matter）から、以下の情報を抽出します。
    *   タイトル (Title)
    *   本文 (Body)
    *   ラベル (Labels)
    *   担当者 (Assignees)
    *   その他、GitHub Issueでサポートされる任意のメタデータ
*   **エラーハンドリング:**
    *   Issueの作成に失敗した場合、対象のファイルは `/_in_box/` から `/_failed_box/` に移動されます。
    *   エラーメッセージやスタックトレースはワークフローのログに出力され、問題の特定に役立てます。

## 4. ファイル移動とコミット

*   **成功時の移動:** Issueの作成が成功したファイルは `/_in_box/` から `/_done_box/` に移動します。
*   **失敗時の移動:** Issueの作成に失敗したファイルは `/_in_box/` から `/_failed_box/` に移動します。
*   **自動コミット:** ファイル移動による変更は、新しいコミットとして `main` ブランチにプッシュされます。
    *   この自動コミットは、当ワークフローのトリガー条件（`on: pull_request`）を満たさないため、無限ループを発生させることはありません。
*   **コミットメッセージ規約:**
    *   自動コミットのメッセージは、どのIssueファイルが処理されたか、成功したか失敗したか、移動先のフォルダを明確に示します。（例: `feat: process issue file <filename> to _done_box`）

## 5. ワークフローの分離

*   **独立したワークフローファイル:** Issue起票ワークフローは、既存のCIワークフロー（`pull_request` イベント時に `pre-commit` を実行）とは**独立した別の `.github/workflows/` ディレクトリ内のYAMLファイル**として定義されます。
*   **責務の分離:** CIはコードの品質保証に専念し、Issue起票ワークフローはIssueファイルの処理に専念することで、各ワークフローの責務を明確にします。

## 6. 認証要件

*   GitHub Actions は、`GITHUB_TOKEN` を使用して GitHub API にアクセスし、Issueの作成やファイルのコミットを行います。
*   `GITHUB_TOKEN` には、Issueの作成、リポジトリコンテンツの読み書きを行うための適切な権限が必要です。通常、デフォルトの `GITHUB_TOKEN` はこれらの権限を保持しています。
