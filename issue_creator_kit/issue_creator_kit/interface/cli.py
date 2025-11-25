import argparse
import logging
import os
import re
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
    parser.add_argument("--pr-number", type=int, help="Pull request number.")

    # First-pass parsing to see if --pr-number is provided
    args, remaining_argv = parser.parse_known_args()

    # If --pr-number is not given, try to get it from GITHUB_REF
    if args.pr_number is None:
        github_ref = os.getenv("GITHUB_REF")
        if github_ref:
            pr_match = re.match(r"refs/pull/(\d+)/merge", github_ref)
            if pr_match:
                args.pr_number = int(pr_match.group(1))

    # Final validation
    if not args.token or not args.repo or args.pr_number is None:
        parser.print_help()
        sys.exit(1)

    try:
        github_service = GithubService(github_token=args.token, repo_full_name=args.repo)
        issue_creation_service = IssueCreationService(github_service)
        moved_files = issue_creation_service.create_issues_from_inbox(pull_number=args.pr_number)

        if moved_files:
            print("moved_files=true")  # noqa: T201

    except Exception as e:
        logger.error(f"Error during Issue Creator execution: {e}", exc_info=True)
        print(f"An unexpected error occurred: {type(e).__name__} - {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    logger.info("Issue Creator CLI finished.")

if __name__ == "__main__":
    main()

