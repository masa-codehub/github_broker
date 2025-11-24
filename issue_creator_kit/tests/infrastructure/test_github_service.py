
from unittest.mock import Mock, patch

import github
import pytest

from issue_creator_kit.infrastructure.github_service import GithubService


class TestGithubService:

    @pytest.fixture
    def mock_github_lib(self):
        with patch('issue_creator_kit.infrastructure.github_service.Github') as mock_github:
            mock_g_instance = mock_github.return_value
            mock_repo = mock_g_instance.get_repo.return_value
            yield mock_g_instance, mock_repo

    @pytest.fixture
    def github_service(self, mock_github_lib):
        # We need to instantiate the service to test its methods,
        # but the actual Github object is patched.
        return GithubService(github_token="fake_token", repo_full_name="owner/repo")

    def test_init(self, github_service, mock_github_lib):
        mock_g_instance, mock_repo = mock_github_lib

        # Test that Github was initialized with the token
        mock_g_instance.get_repo.assert_called_once_with("owner/repo")
        assert github_service.g is mock_g_instance
        assert github_service.repo is mock_repo

    def test_get_pr_files(self, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib
        mock_pr = mock_repo.get_pull.return_value
        mock_files = [Mock(), Mock()]
        mock_pr.get_files.return_value = mock_files

        files = github_service.get_pr_files(pull_number=123)

        mock_repo.get_pull.assert_called_once_with(123)
        assert files == mock_files

    def test_create_issue_success(self, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib
        mock_issue = mock_repo.create_issue.return_value
        mock_issue.html_url = "http://issue.url"

        issue = github_service.create_issue(title="Test", body="Body", labels=["l1"], assignees=["a1"])

        mock_repo.create_issue.assert_called_once_with(title="Test", body="Body", labels=["l1"], assignees=["a1"])
        assert issue == mock_issue

    def test_create_issue_failure(self, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib
        mock_repo.create_issue.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            github_service.create_issue("Test", "Body")

    def test_get_file_content_success(self, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib
        mock_contents = mock_repo.get_contents.return_value
        mock_contents.decoded_content = b"file content"

        content = github_service.get_file_content("path/to/file", "some_ref")

        mock_repo.get_contents.assert_called_once_with("path/to/file", ref="some_ref")
        assert content == "file content"

    def test_get_file_content_not_found(self, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib
        mock_repo.get_contents.side_effect = github.UnknownObjectException(status=404, data={}, headers={})

        content = github_service.get_file_content("path/to/file", "some_ref")

        assert content is None

    @patch('issue_creator_kit.infrastructure.github_service.InputGitTreeElement')
    def test_move_file(self, mock_input_git_tree_element, github_service, mock_github_lib):
        _, mock_repo = mock_github_lib

        # Mocks for git objects
        mock_branch = mock_repo.get_branch.return_value
        mock_branch.commit.sha = "head_sha"
        mock_new_blob = mock_repo.create_git_blob.return_value
        mock_new_blob.sha = "new_blob_sha"
        mock_new_commit = mock_repo.create_git_commit.return_value
        mock_new_commit.sha = "new_commit_sha"
        mock_ref = mock_repo.get_git_ref.return_value

        # Call the method
        commit = github_service.move_file("old/path", "new/path", "commit msg", "content")

        # Assertions
        mock_repo.get_branch.assert_called_once_with(github_service.default_branch)
        mock_repo.get_git_tree.assert_called_once_with("head_sha")
        mock_repo.create_git_blob.assert_called_once_with("content", "utf-8")

        assert mock_input_git_tree_element.call_count == 2

        mock_repo.create_git_tree.assert_called_once()
        mock_repo.get_git_commit.assert_called_once_with("head_sha")
        mock_repo.create_git_commit.assert_called_once()
        mock_repo.get_git_ref.assert_called_once_with(f"heads/{github_service.default_branch}")
        mock_ref.edit.assert_called_once_with(sha="new_commit_sha")

        assert commit == mock_new_commit

