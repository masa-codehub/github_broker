# 入力ファイル仕様 / Input File Specification

このドキュメントは、`_in_box/` ディレクトリに配置されるIssueファイルの厳密なフォーマットを定義します。
IssueファイルはYAML Front MatterとMarkdown本文で構成され、GitHub Issueの自動起票に使用されます。

## 1. ファイル名規則

ファイル名は任意ですが、内容を簡潔に表すスネークケースを推奨します。拡張子は `.md` とします。

例: `new_feature_request.md`, `bug_report_20251121.md`

## 2. ファイル構造

Issueファイルは、ファイルの冒頭にYAML Front Matterを、その後にMarkdown形式の本文を記述します。

```yaml
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

| キー名           | データ型        | 必須/任意 | 説明                                                                 | 例                                                       |
| :--------------- | :-------------- | :-------- | :------------------------------------------------------------------- | :------------------------------------------------------- |
| `title`          | string          | 必須      | Issueのタイトル                                                      | `title: 新機能: ユーザー登録機能`                        |
| `labels`         | array<string>   | 必須      | Issueに付与するラベルのリスト。<br>以下の3種類のラベルを**必ず**含むこと。<br>1. Issueタイプ (`epic`, `story`, `task`)<br>2. 担当エージェント (例: `BACKENDCODER`)<br>3. 優先度 (`P0`～`P4`) | `labels: [story, BACKENDCODER, P2]`                      |
| `related_issues` | array<int>      | 任意      | 関連するIssue番号のリスト                                            | `related_issues: [123, 456]`                             |

### 4. ラベルによる属性定義

`issue_creator_kit`では、Issueの属性（タイプ、優先度、担当者）を全て `labels` 内のタグで管理します。

- **Issueタイプ:**
  - `epic`: Epicとして起票されます。`_in_box`直下のディレクトリに対応します。
  - `story`: Storyとして起票されます。Epicディレクトリ直下のサブディレクトリに対応します。
  - `task`: Taskとして起票されます。Storyディレクトリ配下のファイルに対応します。

- **優先度 (Priority):**
  - `P0` (Critical) ～ `P4` (Low) のいずれかを指定します。

- **担当エージェント (Role):**
  - システムで定義された有効なエージェントロール（`PRODUCT_MANAGER`, `BACKENDCODER` など）を指定します。

### 具体例

```yaml
---
title: 新機能の提案 - 記事のコメント機能
labels:
  - story
  - FRONTENDCODER
  - P2
related_issues:
  - 101
---

# 記事コメント機能の概要
...
```