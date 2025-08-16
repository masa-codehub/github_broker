import os
from github import Github

repo_name = os.getenv("GITHUB_REPOSITORY")
token = os.getenv("GH_TOKEN")

if not repo_name or not token:
    import sys
    print("Error: GITHUB_REPOSITORY and GH_TOKEN environment variables must be set.", file=sys.stderr)
    sys.exit(1)

issue_title = "Assignable Test Issue"
issue_body = """
This is a test issue that should be assigned.

## ブランチ名
feature/assignable-test

## 成果物
- `test.txt`
"""

try:
    g = Github(token)
    repo = g.get_repo(repo_name)
    issue = repo.create_issue(title=issue_title, body=issue_body)
    print(f"Successfully created issue #{issue.number}: {issue.title}")
except Exception as e:
    print(f"Error creating issue: {e}")
