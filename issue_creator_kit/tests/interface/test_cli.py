import sys
from unittest.mock import patch

from issue_creator_kit.interface import cli


@patch('issue_creator_kit.interface.cli.IssueCreationService')
@patch('issue_creator_kit.interface.cli.GithubService')
def test_main_with_args(mock_github_service, mock_issue_creation_service):
    """Test CLI runs successfully with command-line arguments."""
    with patch.object(sys, 'argv', [
        'issue-creator',
        '--token', 'fake_token',
        '--repo', 'owner/repo',
        '--pr-number', '123'
    ]):
        cli.main()

    mock_github_service.assert_called_once_with(github_token='fake_token', repo_full_name='owner/repo')
    mock_issue_creation_service.assert_called_once_with(mock_github_service.return_value)
    mock_issue_creation_service.return_value.create_issues_from_inbox.assert_called_once_with(pull_number=123)

@patch('issue_creator_kit.interface.cli.IssueCreationService')
@patch('issue_creator_kit.interface.cli.GithubService')
@patch.dict('os.environ', {
    'GITHUB_TOKEN': 'env_token',
    'GITHUB_REPOSITORY': 'env/repo',
    'GITHUB_REF': 'refs/pull/456/merge'
})
def test_main_with_env_vars(mock_github_service, mock_issue_creation_service):
    """Test CLI runs successfully using environment variables."""
    with patch.object(sys, 'argv', ['issue-creator']):
        cli.main()

    mock_github_service.assert_called_once_with(github_token='env_token', repo_full_name='env/repo')
    mock_issue_creation_service.assert_called_once_with(mock_github_service.return_value)
    mock_issue_creation_service.return_value.create_issues_from_inbox.assert_called_once_with(pull_number=456)

@patch('sys.exit')
@patch('argparse.ArgumentParser.print_help')
def test_main_missing_args(mock_print_help, mock_exit):
    """Test CLI exits if required arguments are missing."""
    with patch.object(sys, 'argv', ['issue-creator']):
        cli.main()

    mock_print_help.assert_called_once()
    mock_exit.assert_called_once_with(1)

@patch('issue_creator_kit.interface.cli.logger')
@patch('issue_creator_kit.interface.cli.IssueCreationService', side_effect=Exception("Service Error"))
@patch('issue_creator_kit.interface.cli.GithubService')
@patch('sys.exit')
def test_main_exception_handling(mock_exit, mock_github_service, mock_issue_creation_service, mock_logger):
    """Test that the CLI logs an error and exits when an exception occurs."""
    with patch.object(sys, 'argv', [
        'issue-creator',
        '--token', 'fake_token',
        '--repo', 'owner/repo',
        '--pr-number', '123'
    ]):
        cli.main()

    mock_logger.error.assert_called_once()
    mock_exit.assert_called_once_with(1)
