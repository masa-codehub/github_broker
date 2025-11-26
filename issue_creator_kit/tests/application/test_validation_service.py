from pathlib import Path

import pytest

from issue_creator_kit.application.exceptions import FrontmatterError
from issue_creator_kit.application.validation_service import ValidationService


# pytest.mark.parametrize を使用して、可読性とメンテナンス性を向上
@pytest.mark.parametrize(
    "file_content, expected_exception, error_message",
    [
        # Existing tests
        ("no frontmatter here", FrontmatterError, "Frontmatter is missing or invalid."),
        ("---\n---\nno title", FrontmatterError, "Required 'title' field is missing in frontmatter."),
        ("---\ntitle: ''\n---\nempty title", FrontmatterError, "Required 'title' field cannot be empty."),
        ("---\ntitle: 'Valid Title'\nlabels: 'not-a-list'\n---\n", FrontmatterError, "'labels' field must be a list of strings."),
        ("---\ntitle: 'Valid Title'\nrelated_issues: ['not-a-number']\n---\n", FrontmatterError, "'related_issues' field must be a list of integers."),

        # New tests from review
        ("---\ntitle: '   '\n---\nwhitespace title", FrontmatterError, "Required 'title' field cannot be empty."),
        ("\n---\ntitle: 'Valid'\n---\n", FrontmatterError, "Frontmatter is missing or invalid."),
        ("---\ntitle: [invalid yaml\n---\n", FrontmatterError, "Frontmatter is missing or invalid."),
        ("---\ntitle: 'Valid'\nlabels: ['bug', 123]\n---\n", FrontmatterError, "'labels' field must be a list of strings."),
        ("---\ntitle: 'Valid'\nrelated_issues: [123, 1.23]\n---\n", FrontmatterError, "'related_issues' field must be a list of integers."),
        ("---\ntitle: 123\n---\n", FrontmatterError, "Required 'title' field must be a string."),

        # Valid case
        ("---\ntitle: 'Valid Title'\nlabels: ['bug', 'P1']\nrelated_issues: [123, 456]\n---\nValid content", None, None),
    ],
)
def test_validate_frontmatter(tmp_path: Path, file_content: str, expected_exception, error_message):
    """
    ADR-019で定義されたフロントマターの検証ルールをテストする。
    """
    # テスト用のMarkdownファイルを動的に生成
    p = tmp_path / "test_document.md"
    p.write_text(file_content)

    # サービスインスタンスを作成
    service = ValidationService()

    if expected_exception:
        # 例外が送出されることを確認
        with pytest.raises(expected_exception) as excinfo:
            service.validate_frontmatter(str(p))
        # エラーメッセージが期待通りであることを確認
        assert error_message in str(excinfo.value)
    else:
        # 例外が送出されないことを確認
        try:
            service.validate_frontmatter(str(p))
        except FrontmatterError as e:
            pytest.fail(f"Unexpected exception raised: {e}")
