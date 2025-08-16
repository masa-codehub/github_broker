import os
from github_broker.infrastructure.github_client import GitHubClient

repo_name = os.getenv("GITHUB_REPOSITORY")
issue_number = 25

client = GitHubClient()
try:
    repo = client._client.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    print(f"Issue Title: {issue.title}")
    print(f"Issue Number: {issue.number}")
    print(f"Labels: {[label.name for label in issue.labels]}")
    print("--- BODY ---")
    print(issue.body)
except Exception as e:
    print(f"Error getting issue info: {e}")
