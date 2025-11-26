
from github_broker.infrastructure.document_validation.document_validator import (
    validate_frontmatter,
)


def test_validate_frontmatter_valid():
    content = """---
title: "Test Title"
labels: ["test", "bug"]
assignees: ["user1", "user2"]
---
Some content
"""
    errors = validate_frontmatter(content)
    assert not errors

def test_validate_frontmatter_no_frontmatter():
    content = "Some content without frontmatter"
    errors = validate_frontmatter(content)
    assert "No YAML front matter found." in errors

def test_validate_frontmatter_invalid_yaml():
    content = """---
title: "Test Title"
labels: ["test", "bug"
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "Error parsing YAML front matter" in errors[0]

def test_validate_frontmatter_not_a_dictionary():
    content = """---
- "item1"
- "item2"
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "YAML front matter is not a valid dictionary." in errors

def test_validate_frontmatter_missing_title():
    content = """---
labels: ["test", "bug"]
assignees: ["user1", "user2"]
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "Missing required key in front matter: 'title'" in errors

def test_validate_frontmatter_title_not_string():
    content = """---
title: 123
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'title' must be a string." in errors

def test_validate_frontmatter_title_empty_string():
    content = """---
title: " "
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'title' must be a non-empty string." in errors

def test_validate_frontmatter_labels_not_list():
    content = """---
title: "Test Title"
labels: "test"
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'labels' must be a list of strings." in errors

def test_validate_frontmatter_labels_not_list_of_strings():
    content = """---
title: "Test Title"
labels: ["test", 123]
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'labels' must be a list of strings." in errors

def test_validate_frontmatter_assignees_not_list():
    content = """---
title: "Test Title"
assignees: "user1"
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'assignees' must be a list of strings." in errors

def test_validate_frontmatter_assignees_not_list_of_strings():
    content = """---
title: "Test Title"
assignees: ["user1", 123]
---
Some content
"""
    errors = validate_frontmatter(content)
    assert "'assignees' must be a list of strings." in errors

def test_validate_frontmatter_optional_keys_missing():
    content = """---
title: "Test Title"
---
Some content
"""
    errors = validate_frontmatter(content)
    assert not errors

def test_validate_frontmatter_empty_lists():
    content = """---
title: "Test Title"
labels: []
assignees: []
---
Some content
"""
    errors = validate_frontmatter(content)
    assert not errors
