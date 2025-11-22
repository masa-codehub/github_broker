from unittest.mock import Mock, patch

import github
import pytest

from github_broker.infrastructure.github_actions.github_client_for_issue_creator import (
    GitHubClientForIssueCreator,
)


class TestGitHubClientForIssueCreator:

    @pytest.fixture
    def mock_github_objects(self):
        mock_g = Mock()
        mock_repo = Mock()
        mock_g.get_user.return_value.get_repo.return_value = mock_repo
        return mock_g, mock_repo

    @pytest.fixture
    def client(self, mock_github_objects):
        mock_g, mock_repo = mock_github_objects
        return GitHubClientForIssueCreator("fake_token", mock_repo, "main")

    def test_create_issue_success(self, client):
        mock_issue = Mock()
        mock_issue.html_url = "http://issue_url"
        client.repo.create_issue.return_value = mock_issue

        title = "Test Issue"
        body = "Test Body"
        labels = ["bug"]
        assignees = ["user"]

        issue = client.create_issue(title, body, labels, assignees)

        client.repo.create_issue.assert_called_once_with(title=title, body=body, labels=labels, assignees=assignees)
        assert issue == mock_issue

    def test_create_issue_no_labels_assignees(self, client):
        mock_issue = Mock()
        mock_issue.html_url = "http://issue_url"
        client.repo.create_issue.return_value = mock_issue

        title = "Test Issue"
        body = "Test Body"

        issue = client.create_issue(title, body)

        client.repo.create_issue.assert_called_once_with(title=title, body=body, labels=[], assignees=[])
        assert issue == mock_issue

    def test_create_issue_failure(self, client):
        client.repo.create_issue.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            client.create_issue("Title", "Body")

        client.repo.create_issue.assert_called_once()

    def test_get_file_content_success(self, client):
        mock_contents = Mock()
        mock_contents.decoded_content = b"file content"
        client.repo.get_contents.return_value = mock_contents

        content = client.get_file_content("path/to/file.txt", "sha")
        assert content == "file content"
        client.repo.get_contents.assert_called_once_with("path/to/file.txt", ref="sha")

    def test_get_file_content_not_found(self, client):
        client.repo.get_contents.side_effect = github.UnknownObjectException(404, Mock(), Mock())

        content = client.get_file_content("path/to/nonexistent.txt", "sha")
        assert content is None
        client.repo.get_contents.assert_called_once_with("path/to/nonexistent.txt", ref="sha")

    @patch('github_broker.infrastructure.github_actions.github_client_for_issue_creator.InputGitTreeElement')
    def test_move_file_new_file_and_delete_old(self, mock_input_git_tree_element, client):
        # Configure the mock_input_git_tree_element to return a mock object
        # that has the path and sha attributes set based on the call.
        def create_mock_element(path, mode, type, sha):
            mock_element = Mock()
            mock_element.path = path
            mock_element.sha = sha
            return mock_element
        mock_input_git_tree_element.side_effect = create_mock_element
        # Mocking necessary Git objects
        mock_branch = Mock()
        mock_branch.commit.sha = "old_head_sha"
        client.repo.get_branch.return_value = mock_branch

        mock_base_tree = Mock()
        client.repo.get_git_tree.return_value = mock_base_tree

        mock_new_blob = Mock()
        mock_new_blob.sha = "new_blob_sha"
        client.repo.create_git_blob.return_value = mock_new_blob

        mock_new_tree = Mock()
        client.repo.create_git_tree.return_value = mock_new_tree

        mock_parent_commit = Mock()
        client.repo.get_git_commit.return_value = mock_parent_commit

        mock_new_commit = Mock()
        mock_new_commit.sha = "new_commit_sha"
        client.repo.create_git_commit.return_value = mock_new_commit

        mock_git_ref = Mock()
        client.repo.get_git_ref.return_value = mock_git_ref

        old_file_path = "old/path/file.txt"
        new_file_path = "new/path/file.txt"
        commit_message = "Move file test"
        file_content = "new file content"

        commit = client.move_file(old_file_path, new_file_path, commit_message, file_content)

        client.repo.get_branch.assert_called_once_with("main")
        client.repo.get_git_tree.assert_called_once_with("old_head_sha")
        client.repo.create_git_blob.assert_called_once_with(file_content, "utf-8")

        # Check create_git_tree call
        called_elements = client.repo.create_git_tree.call_args.args[0]
        assert len(called_elements) == 2

        # We need to check the attributes of the InputGitTreeElement objects directly
        # The order of elements might not be guaranteed, so we'll check presence
        new_file_element_found = False
        old_file_element_found = False

        for element in called_elements:
            if element.path == new_file_path and element.sha == "new_blob_sha":
                new_file_element_found = True
            if element.path == old_file_path and element.sha == '':
                old_file_element_found = True

        assert new_file_element_found
        assert old_file_element_found
        client.repo.get_git_commit.assert_called_once_with("old_head_sha")
        client.repo.create_git_commit.assert_called_once_with(commit_message, mock_new_tree, [mock_parent_commit])
        client.repo.get_git_ref.assert_called_once_with("heads/main")
        mock_git_ref.edit.assert_called_once_with(sha="new_commit_sha")
        assert commit == mock_new_commit

    @patch('github_broker.infrastructure.github_actions.github_client_for_issue_creator.InputGitTreeElement')
    def test_move_file_only_update_content(self, mock_input_git_tree_element, client):
        def create_mock_element(path, mode, type, sha):
            mock_element = Mock()
            mock_element.path = path
            mock_element.sha = sha
            return mock_element
        mock_input_git_tree_element.side_effect = create_mock_element
        mock_branch = Mock()
        mock_branch.commit.sha = "old_head_sha"
        client.repo.get_branch.return_value = mock_branch

        mock_base_tree = Mock()
        client.repo.get_git_tree.return_value = mock_base_tree

        mock_new_blob = Mock()
        mock_new_blob.sha = "new_blob_sha"
        client.repo.create_git_blob.return_value = mock_new_blob

        mock_new_tree = Mock()
        client.repo.create_git_tree.return_value = mock_new_tree

        mock_parent_commit = Mock()
        client.repo.get_git_commit.return_value = mock_parent_commit

        mock_new_commit = Mock()
        mock_new_commit.sha = "new_commit_sha"
        client.repo.create_git_commit.return_value = mock_new_commit

        mock_git_ref = Mock()
        client.repo.get_git_ref.return_value = mock_git_ref

        file_path = "path/to/file.txt"
        commit_message = "Update file content"
        file_content = "updated content"

        commit = client.move_file(file_path, file_path, commit_message, file_content) # same old_file_path and new_file_path

        # Check create_git_tree call
        called_elements = client.repo.create_git_tree.call_args.args[0]
        assert len(called_elements) == 1

        # We need to check the attributes of the InputGitTreeElement object directly
        element = called_elements[0]
        assert element.path == file_path
        assert element.sha == "new_blob_sha"

        assert commit == mock_new_commit
