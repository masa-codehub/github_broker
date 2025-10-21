# [Design Doc 002] ドキュメントフォーマット検証スクリプト (Document Format Validator Script)

- **Status**: Draft
- **Date**: 2025-10-21
- **Author**: CONTENTS_WRITER (Acting as TECHNICAL_DESIGNER)
- **Source ADR**: [ADR-012] 主要ドキュメントのフォーマット検証をCIに統合

## 1. 目的 (Purpose)

本設計書は、[ADR-012]で決定された、主要なMarkdownドキュメントのフォーマット、命名規則、フォルダ構成を自動的に検証するPythonスクリプトの実装に先立ち、その技術的な詳細設計を定義することを目的とする。これにより、ドキュメントの品質と一貫性を自動的に保証し、レビュアーの負担を軽減する。

## 2. 設計の概要 (Design Overview)

検証スクリプトは、プロジェクトのユーティリティスクリプト群として `scripts/document_validator.py` に配置される。
このスクリプトは、`pre-commit` フックを通じて実行され、引数として渡されたファイルリストに対して、命名規則、フォルダ構造、必須セクションの存在を検証する。

## 3. 技術的な詳細 (Technical Details)

### 3.1. エントリーポイント: `main()` 関数

- **責務:** CLIからの実行を受け付け、検証プロセス全体を統括する。
- **処理フロー:**
    1.  CLI引数として渡された検証対象のファイルリスト（`pre-commit` から渡される）を取得する。
    2.  各ファイルに対して `validate_file()` を呼び出す。
    3.  検証中にエラーが検出された場合、エラーメッセージを標準エラー出力 (`sys.stderr`) に出力する。
    4.  全てのエラーを収集した後、エラーが一つでもあれば非ゼロの終了コード (`sys.exit(1)`) で終了する。
    5.  エラーがなければ、正常終了コード (`sys.exit(0)`) で終了する。

### 3.2. ファイル検証: `validate_file(filepath)` 関数

- **責務:** 単一のファイルパスを受け取り、そのファイルに対して全ての検証ルールを適用する。
- **処理フロー:**
    1.  `check_naming_convention(filepath)` を実行。
    2.  `check_folder_structure(filepath)` を実行。
    3.  `check_required_sections(filepath)` を実行。
    4.  検出された全てのエラーメッセージのリストを返す。

### 3.3. ルールチェック関数群 (Rule Checkers)

#### 3.3.1. `check_naming_convention(filepath)`

- **責務:** `plans` 配下のファイル名が、規約に沿った接頭辞を持つか検証する。
- **ロジック:**
    - ファイルパスが `plans/` 配下にある場合のみ実行。
    - ファイル名が `epic-`, `story-`, `task-` のいずれかで始まっているかチェックする。

#### 3.3.2. `check_folder_structure(filepath)`

- **責務:** `plans` 配下のファイルが、ファイル名と一致する適切なサブディレクトリに配置されているか検証する。
- **ロジック:**
    - ファイル名が `story-*` で始まる場合、そのファイルが `plans/*/stories/` の形式のサブディレクトリ内に存在するかチェックする。
    - ファイル名が `task-*` で始まる場合、そのファイルが `plans/*/tasks/` の形式のサブディレクトリ内に存在するかチェックする。

#### 3.3.3. `check_required_sections(filepath)`

- **責務:** ファイルの内容を読み込み、ドキュメントタイプに応じた必須セクション（Markdownヘッダー）が全て存在するか検証する。
- **ロジック:**
    - ファイルパスからドキュメントタイプ（例: ADR, Design Doc, Epic/Story/Task）を特定する。
    - ドキュメントタイプに対応する**必須セクションリスト**（例: ADRの場合は `## Context (背景)`, `## Decision (決定)`, `## Consequences (結果)` など）を取得する。
    - ファイル内容を解析し、必須セクションが全て含まれているかチェックする。

### 3.4. エラー出力の仕様 (Error Output Specification)

検証スクリプトは、規約違反を検知した場合、開発者が迅速に問題を特定し修正できるように、以下のフォーマットでエラーメッセージを標準エラー出力 (`sys.stderr`) に出力する。

- **フォーマット:** `ERROR: <filepath> - <Violation Type>: <Details>`
- **具体例:**
    ```
    ERROR: plans/adr-012/story-test.md - Folder Structure Violation: 'story-*' files must be in 'stories/' subdirectory.
    ERROR: docs/adr/013-new-adr.md - Missing Required Section: '## Decision (決定)'
    ```

### 3.5. pre-commitへの統合方法 (Integration with pre-commit)

検証スクリプトは、ローカルでのコミット時およびCIでの自動検証のために、`.pre-commit-config.yaml` に以下の設定でフックとして統合される。

```yaml
# .pre-commit-config.yaml への追加設定 (予定)
- repo: local
  hooks:
    - id: document-validator
      name: Document Format Validator
      entry: python scripts/document_validator.py
      language: system
      types: [markdown]
      files: |
        (?x)^(
          docs/adr/.*\.md|
          docs/design-docs/.*\.md|
          plans/.*\.md
        )$
      pass_filenames: true # pre-commitから渡されたファイルのみを検証対象とする
```

この設定により、指定されたMarkdownファイルが変更された場合、`scripts/document_validator.py` が実行され、非ゼロの終了コードが返された場合はコミットがブロックされる。

### 3.6. 必須セクションの定義 (Definition of Required Sections)

`check_required_sections` 関数で使用される、ドキュメントタイプごとの必須セクションの定義（初期案）。

| ドキュメントタイプ | パスパターン | 必須セクション (Markdown Header) |
| :--- | :--- | :--- |
| **ADR** | `docs/adr/*.md` | `# [ADR-XXX] Title`, `## Context (背景)`, `## Decision (決定)`, `## Consequences (結果)` |
| **Design Doc** | `docs/design-docs/*.md` | `# [Design Doc XXX] Title`, `## 1. 目的 (Purpose)`, `## 2. 設計の概要 (Design Overview)`, `## 3. 技術的な詳細 (Technical Details)` |
| **Epic** | `plans/epic-*.md` | `# Epic: Title`, `## 目的 (Goal)`, `## 関連するストーリー (Related Stories)` |
| **Story** | `plans/*/stories/story-*.md` | `# Story: Title`, `## As a... I want... So that...`, `## 完了条件 (Acceptance Criteria)` |
| **Task** | `plans/*/tasks/task-*.md` | `# Task: Title`, `## 目的 (Goal)`, `## 手順 (Steps)` |
