```mermaid
flowchart TD
    %% Swimlanes
    subgraph 開発者
        A[変更を伴うPull Request作成] --> B[Pull RequestをOpen]
        B --> C{ファイルは_in_box/ にあるか？}
        C -- Yes --> D[pre-commitフックでIssueファイルの形式を検証]
        C -- No --> E[通常の開発プロセス]
        D -- 検証成功 --> F[PRレビュー・承認を経てmainブランチにマージ]
        E --> F
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