```mermaid
flowchart TD
    %% Swimlanes
    subgraph 開発者
        A[コード変更とIssueファイルをローカルでコミット] -- "git commit" --> B[pre-commitフックでIssueファイルの形式を検証]
        B -- 検証成功 --> C[Pull Requestを作成]
        B -- 検証失敗 --> A
        C --> D{ファイルは_in_box/ にあるか？}
        D -- Yes --> E[PRレビュー・承認を経てmainブランチにマージ]
        D -- No --> F[通常の開発プロセス]
        F --> E
    end

    subgraph GitHub (System)
        F -- "GitHub Actions: ワークフローをトリガー" --> G{マージされたPRに_in_box/ファイルがあるか？}
    end

    subgraph Issue自動起票ワークフロー
        G -- Yes --> I[Issueファイルを読み込み]
        I --> J[Issue情報を抽出]
        J --> K{GitHub Issueの作成は成功したか？}
        K -- Yes --> L[Issueファイルを_done_box/に移動]
        K -- No --> M[Issueファイルを_failed_box/に移動]
        L --> N[ファイル移動を新しいコミットとしてmainにプッシュ]
        M --> N
        N --> O(完了)
        G -- No --> P(何もしない)
        P --> O
    end
```