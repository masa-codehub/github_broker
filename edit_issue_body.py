import os
from github import Github

repo_name = os.getenv("GITHUB_REPOSITORY")
issue_number = 25
token = os.getenv("GH_TOKEN")

# --- 新しい本文の内容 ---
new_body = """
### 課題
現在の`TaskService`には単体テストが存在しません。そのため、ロジックの変更時に、今回発生したような単純な構文エラーや、Issueの本文を解析する`_parse_issue_body`メソッドの不具合などを事前に検知できません。

### 提案
`pytest`と`unittest.mock`を使用し、`TaskService`の主要なロジックに対する単体テストを`tests/application/test_task_service.py`に実装します。

**検証すべきシナリオ:**

1.  **`_parse_issue_body`のテスト:**
    -   正常な本文（`## ブランチ名`と`## 成果物`が存在）を正しく解析できること。
    -   どちらかのセクションが欠けている場合に`None`を返すこと。
    -   改行コードが`\r\n`の場合でも正しく解析できること。
    -   本文が空、または`None`の場合にエラーなく`None`を返すこと。

2.  **`request_task`のテスト（モックを使用）:**
    -   **正常系:** 新しいタスクが見つかり、正しく割り当てられること（ラベル追加、ブランチ作成など）。
    -   **正常系（前タスクあり）:** `_process_previous_task`が呼び出され、前タスクのラベルが`needs-review`に変更されること。
    -   **異常系:** 割り当てるタスクが見つからなかった場合に`None`を返すこと。
    -   **異常系:** Redisロックが取得できなかった場合に例外を発生させること。

### 完了の定義
- `TaskService`の主要なメソッドが、上記シナリオに基づいてテストされていること。
- `pytest`で全てのテストが成功すること。

## ブランチ名
feature/issue-25-add-taskservice-tests

## 成果物
- `tests/application/test_task_service.py`
"""

try:
    g = Github(token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    issue.edit(body=new_body)
    print(f"Successfully updated body for issue #{issue_number}")
except Exception as e:
    print(f"Error updating issue: {e}")
