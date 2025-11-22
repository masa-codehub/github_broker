from unittest.mock import Mock, patch

import github

from github_broker.infrastructure.github_actions.github_action_utils import (
    create_issue,
    get_default_branch,
    get_file_content,
    get_github_repo,
    get_pr_files,
)


class TestGitHubActionUtils:

    @patch('github_broker.infrastructure.github_actions.github_action_utils.Github')
    def test_get_github_repo(self, mock_github_class):
        mock_g = Mock()
        mock_github_class.return_value = mock_g
        mock_repo = Mock()
        mock_g.get_user.return_value.get_repo.return_value = mock_repo

        repo_full_name = "owner/repo_name"
        github_token = "fake_token"
        result = get_github_repo(repo_full_name, github_token)

        mock_github_class.assert_called_once_with(github_token)
        mock_g.get_user.assert_called_once()
        mock_g.get_user.return_value.get_repo.assert_called_once_with("repo_name")
        assert result == mock_repo

    def test_get_default_branch(self):
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        result = get_default_branch(mock_repo)
        assert result == "main"

    def test_get_pr_files(self):
        mock_repo = Mock()
        mock_pr = Mock()
        mock_file1 = Mock()
        mock_file1.filename = "file1.txt"
        mock_file2 = Mock()
        mock_file2.filename = "file2.txt"
        mock_pr.get_files.return_value = [mock_file1, mock_file2]
        mock_repo.get_pull.return_value = mock_pr

        pull_number = 1
        result = get_pr_files(mock_repo, pull_number)

        mock_repo.get_pull.assert_called_once_with(pull_number)
        mock_pr.get_files.assert_called_once()
        assert result == [mock_file1, mock_file2]

    def test_get_file_content(self):
        mock_repo = Mock()
        mock_contents = Mock()
        mock_contents.decoded_content = b"file content"
        mock_repo.get_contents.return_value = mock_contents

        file_path = "path/to/file.txt"
        ref = "sha"
        result = get_file_content(mock_repo, file_path, ref)

        mock_repo.get_contents.assert_called_once_with(file_path, ref=ref)
        assert result == "file content"

    def test_get_file_content_not_found(self):
        mock_repo = Mock()
        mock_repo.get_contents.side_effect = github.UnknownObjectException(404, Mock(), Mock())

        file_path = "path/to/nonexistent.txt"
        ref = "sha"
        result = get_file_content(mock_repo, file_path, ref)

        assert result is None

    def test_create_issue(self):
        mock_repo = Mock()
        mock_issue = Mock()
        mock_repo.create_issue.return_value = mock_issue

        title = "Test Issue"
        body = "Test Body"
        labels = ["bug"]
        assignees = ["user"]
        result = create_issue(mock_repo, title, body, labels, assignees)

        mock_repo.create_issue.assert_called_once_with(title=title, body=body, labels=labels, assignees=assignees)
        assert result == mock_issue
