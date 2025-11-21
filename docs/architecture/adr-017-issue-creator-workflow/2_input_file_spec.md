# 入力ファイル仕様 / Input File Specification

このドキュメントは、`/_in_box` ディレクトリに配置されるIssueファイルの厳密なフォーマットを定義します。
IssueファイルはYAML Front MatterとMarkdown本文で構成され、GitHub Issueの自動起票に使用されます。

## 1. ファイル名規則

ファイル名は任意ですが、内容を簡潔に表すスネークケースを推奨します。拡張子は `.md` とします。

例: `new_feature_request.md`, `bug_report_20251121.md`

## 2. ファイル構造

Issueファイルは、ファイルの冒頭にYAML Front Matterを、その後にMarkdown形式の本文を記述します。

```
---
key: value
another_key: another_value
---

# Markdown本文
これはIssueの本文として使用されます。
詳細な説明や関連情報を含めることができます。
```

## 3. YAML Front Matter 仕様

YAML Front Matterは、Issueのメタデータを定義するために使用されます。以下のキーがサポートされます。

| キー名     | データ型   | 必須/任意 | 説明                                                           | 例                                                      |
| :--------- | :--------- | :-------- | :------------------------------------------------------------- | :------------------------------------------------------ |
| `title`    | string     | 必須      | Issueのタイトル                                                | `title: 新機能: ユーザー登録機能`                       |
| `labels`   | array<string> | 任意      | Issueに付与するラベルのリスト                                  | `labels: [feature, backend]`                            |
| `assignees`| array<string> | 任意      | Issueの担当者のGitHubユーザー名のリスト                        | `assignees: [octocat, monalisa]`                        |
| `milestone`| string / number | 任意      | Issueを関連付けるマイルストーンの名前または番号               | `milestone: Sprint 1` or `milestone: 1`                 |
| `due_date` | string (YYYY-MM-DD) | 任意      | Issueの期限 (日付のみ)                                         | `due_date: 2025-12-31`                                  |
| `priority` | string     | 任意      | Issueの優先度 (例: `high`, `medium`, `low`)                    | `priority: high`                                        |
| `epic_id`  | string     | 任意      | 関連するEpicのID                                               | `epic_id: epic-123`                                     |
| `issue_type` | string     | 任意      | Issueのタイプ (例: `bug`, `task`, `story`)                    | `issue_type: story`                                     |
| `status`   | string     | 任意      | Issueのステータス (例: `open`, `in progress`, `closed`)       | `status: open`                                          |

### 具体例

```yaml
---
title: 新機能の提案 - 記事のコメント機能
labels: [feature, frontend, backend]
assignees: [developer-a, developer-b]
milestone: Q4-2025
due_date: 2025-12-25
priority: high
epic_id: EPIC-001
issue_type: story
status: open
---

# 記事コメント機能の概要

## 目的
ユーザーが記事に対してコメントを投稿できるようにすることで、コミュニティの活性化とエンゲージメントの向上を図ります。

## 詳細
- 各記事ページにコメント入力フォームとコメント一覧を表示します。
- ユーザーはログインしている場合のみコメントを投稿できます。
- コメントはMarkdown形式で記述可能とします。
- コメント投稿後、即座にコメント一覧に反映されます。
- 不適切なコメントは報告・削除できる機能を検討します。

## 技術スタック
- フロントエンド: React, TypeScript
- バックエンド: FastAPI, Python
- データベース: PostgreSQL (コメントデータ保存用)

## 考慮事項
- コメントのモデレーション機能
- パフォーマンス最適化 (大量コメント時の表示速度)
- セキュリティ (XSS対策など)
