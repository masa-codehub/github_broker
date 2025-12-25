# プロジェクトディレクトリ構造とドキュメント配置ガイド

このドキュメントは、`github_broker` プロジェクトにおけるディレクトリ構造と、各種ドキュメントの配置ルールを定義します。
ドキュメントと実装の乖離を防ぎ、情報の発見性を高めることを目的としています。

## 基本原則

1. **責務による分離**: コード、ドキュメント、要件定義は、それぞれの責務に基づいて明確に分離されたディレクトリに配置します。
2. **実装との同期**: ドキュメントは常に実装（コード）を正とし、その振る舞いを正確に記述します。
3. **単一情報源 (SSOT)**: 同じ情報は一箇所にのみ記述し、多重管理を防ぎます。

## ディレクトリ構造定義

```
/app
├── docs/                   # [Documentation] 実装に基づくシステム全体のドキュメント
│   ├── architecture/       # アーキテクチャ図 (C4), システム全体の構造
│   ├── specs/              # 詳細仕様書 (API, DB, バリデーションルール)
│   ├── guides/             # 開発者向けガイド, 運用ガイド, このドキュメント
│   └── libs/               # 内部ライブラリごとのドキュメント
│       └── issue_creator_kit/
│
├── reqs/                   # [Requirements] 意思決定の記録 (Whyの記録)
│   ├── adr/                # Architecture Decision Records
│   └── design-docs/        # Design Documents (Epic/Storyごとの設計方針)
│
├── github_broker/          # [Code] メインアプリケーション
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── interface/
│
├── issue_creator_kit/      # [Code] 共有ライブラリ
│   └── (ソースコードのみ配置。ドキュメントは docs/libs/ へ)
│
├── scripts/                # 運用・開発支援スクリプト
├── tests/                  # テストコード
└── README.md               # プロジェクトの入り口
```

## ドキュメント詳細分類

### 1. `docs/` (Documentation)
現在のシステムの「振る舞い (How/What)」を記述します。コードが修正されたら、必ずここも修正する必要があります。

- **`architecture/`**: システム全体の俯瞰図。
    - `c4-model.md`: コンテキスト図、コンテナ図。
    - `system-context.md`: 外部システムとの連携。
- **`specs/`**: 実装の詳細な仕様。
    - `*_api.md`: API仕様書。
    - `database-schema.md`: DB定義。
- **`guides/`**: 手順書、ガイドライン。
    - `development-workflow.md`: 開発フロー。
    - `directory-structure.md`: (本文書)

### 2. `reqs/` (Requirements)
システムが「なぜそうなっているか (Why)」という意思決定の履歴を記述します。これらは原則として**不変**（追記はあっても書き換えはない）です。

- **`adr/`**: 技術的な意思決定。
- **`design-docs/`**: 機能実装時の設計方針。

## リファクタリング方針 (To-be)

本ガイドライン制定に伴い、以下の通りファイルを再配置します。

1. `issue_creator_kit/docs/` 内のコンテンツは `docs/libs/issue_creator_kit/` へ移動。
2. プロジェクトルートにある散発的な `*.md`, `*.txt` は内容を確認し、`docs/` 配下へ移動するか削除。
3. `reqs/` 配下の構造を整理し、古すぎるドキュメントはアーカイブ。
