import pytest

from scripts.validate_docs import validate_adr_summary_format


@pytest.mark.parametrize(
    "content, expected_errors",
    [
        (
            "# 概要 / Summary\n[ADR-123] This is a title",
            [],
        ),
        (
            "# 概要 / Summary\n[ADR-1] Another title",
            [],
        ),
        (
            "# 概要 / Summary\nThis is not a valid summary format.",
            ["ADR summary must be followed by a line in the format '[ADR-xxx]'."],
        ),
        (
            "Some other content\n# Not the summary",
            ["ADR must contain a '# 概要 / Summary' section."],
        ),
        (
            "# 概要 / Summary",
            ["ADR summary must be followed by a line in the format '[ADR-xxx]'."],
        ),
    ],
)
def test_validate_adr_summary_format(content, expected_errors):
    errors = validate_adr_summary_format(content)
    assert errors == expected_errors
