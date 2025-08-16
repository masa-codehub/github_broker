import os
from github_broker.infrastructure.github_client import GitHubClient

repo_name = os.getenv("GITHUB_REPOSITORY")

client = GitHubClient()
try:
    print("Checking for assignable issues...")
    issues = client.get_open_issues(repo_name)
    if issues:
        print(f"Found {len(issues)} assignable issues:")
        for issue in issues:
            print(f"  - #{issue.number}: {issue.title}")
    else:
        print("No assignable issues found.")
except Exception as e:
    print(f"Error checking for issues: {e}")
