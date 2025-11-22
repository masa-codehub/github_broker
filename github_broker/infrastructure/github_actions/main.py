import logging
import os
import re
import sys

from github_broker.infrastructure.github_actions.github_action_utils import (
    get_default_branch,
    get_github_repo,
)
from github_broker.infrastructure.github_actions.github_client_for_issue_creator import (
    GitHubClientForIssueCreator,
)
from github_broker.infrastructure.github_actions.issue_creator import IssueCreator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():
    logger.info("GitHub Issue Creator Action started.")

    github_token = os.getenv("GITHUB_TOKEN")
    repository_name = os.getenv("GITHUB_REPOSITORY")  # Format: owner/repo
    github_ref = os.getenv("GITHUB_REF")  # e.g., refs/pull/123/merge

    # Per review, improve error message.
    missing_vars = []
    if not github_token:
        missing_vars.append("GITHUB_TOKEN")
    if not repository_name:
        missing_vars.append("GITHUB_REPOSITORY")
    if not github_ref:
        missing_vars.append("GITHUB_REF")

    if missing_vars:
        logger.error(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
        sys.exit(1)


    # Extract PR number from GITHUB_REF
    pr_match = re.match(r"refs/pull/(\d+)/merge", github_ref)
    if not pr_match:
        logger.error(f"Error: Could not extract PR number from GITHUB_REF: {github_ref}")
        sys.exit(1)

    pull_number = int(pr_match.group(1))

    try:
        repo = get_github_repo(repository_name, github_token)
        default_branch = get_default_branch(repo)

        # Pass repo object to client, remove unused repository_name
        github_client = GitHubClientForIssueCreator(github_token, repo, default_branch)

        # IssueCreator now handles its own parser import
        issue_creator = IssueCreator(github_client)

        issue_creator.create_issues_from_inbox(pull_number)

    except Exception as e:
        logger.error(f"Error during GitHub Issue Creator Action: {e}", exc_info=True)
        sys.exit(1)

    logger.info("GitHub Issue Creator Action finished.")

if __name__ == "__main__":
    run()
