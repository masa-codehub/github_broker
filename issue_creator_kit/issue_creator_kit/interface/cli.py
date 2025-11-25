import argparse
import logging
import os
import sys

from issue_creator_kit.application.issue_service import IssueCreationService
from issue_creator_kit.infrastructure.github_service import GithubService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Issue Creator CLI started.")

    parser = argparse.ArgumentParser(description="Create GitHub issues from files in a PR's _in_box directory.")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token.")
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY"), help="Repository name in 'owner/repo' format.")

    # Parse arguments from the command line
    args = parser.parse_args()

    # Get the pull request number directly from the environment variable
    pr_number_str = os.getenv("PR_NUMBER")
    pr_number = int(pr_number_str) if pr_number_str else None

    # Final validation
    if not args.token or not args.repo or pr_number is None:
        parser.print_help()
        sys.exit(1)

    try:
        github_service = GithubService(github_token=args.token, repo_full_name=args.repo)
        issue_creation_service = IssueCreationService(github_service)
        moved_files = issue_creation_service.create_issues_from_inbox(pull_number=pr_number)

        if moved_files:
            print("moved_files=true")  # noqa: T201

    except Exception as e:
        logger.error(f"Error during Issue Creator execution: {e}", exc_info=True)
        print(f"An unexpected error occurred: {type(e).__name__} - {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    logger.info("Issue Creator CLI finished.")

if __name__ == "__main__":
    main()

