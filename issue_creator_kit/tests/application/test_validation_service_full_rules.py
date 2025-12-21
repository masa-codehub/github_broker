
import pytest

from issue_creator_kit.application.exceptions import FrontmatterError
from issue_creator_kit.application.validation_service import ValidationService
from issue_creator_kit.domain.document import DocumentType


class TestValidationServiceFullRules:
    @pytest.fixture
    def service(self):
        return ValidationService()

    def test_validate_frontmatter_labels_strict(self, service, tmp_path):
        # Case 1: Missing strictly required labels (epic/story/task)
        content = """---
title: Test Issue
labels: ["invalid_label"]
---
"""
        f = tmp_path / "test_labels.md"
        f.write_text(content, encoding="utf-8")

        with pytest.raises(FrontmatterError, match="'labels' must contain one of 'epic', 'story', 'task'"):
            service.validate_frontmatter(str(f))

    def test_validate_frontmatter_labels_missing_role(self, service, tmp_path):
        content = """---
title: Test Issue
labels: ["epic", "P0"]
---
"""
        f = tmp_path / "test_labels_role.md"
        f.write_text(content, encoding="utf-8")

        with pytest.raises(FrontmatterError, match="'labels' must contain a valid agent role"):
            service.validate_frontmatter(str(f))

    def test_validate_sections_missing_new_headers(self, service):
        content = """
# Test Issue
## 親Issue (Parent Issue)
## 子Issue (Sub-Issues)
## As-is (現状)
## To-be (あるべき姿)
## 完了条件 (Acceptance Criteria)
## 成果物 (Deliverables)
## ブランチ戦略 (Branching Strategy)
"""
        # "## 参照元の意思決定 (Source Decision Document)" and others are missing
        missing = service.validate_sections(content, DocumentType.PLAN)
        assert "## 参照元の意思決定 (Source Decision Document)" in missing
        assert "## 目標達成までの手順 (Steps to Achieve Goal)" in missing

    def test_validate_branching_strategy_content(self, service):
        content = """
## ブランチ戦略 (Branching Strategy)
Just some text.
"""
        metadata = {"labels": ["epic"]}
        errors = service.validate_plan_content(content, metadata)
        assert "Branching Strategy section must contain 'ベースブランチ (Base Branch):'" in errors
        assert "Branching Strategy section must contain '作業ブランチ (Feature Branch):'" in errors

    def test_validate_completion_criteria_content(self, service):
        content = """
## 完了条件 (Acceptance Criteria)
Some criteria.
"""
        metadata = {"labels": ["epic"]}
        errors = service.validate_plan_content(content, metadata)
        assert "Epic completion criteria must contain 'このEpicを構成する全てのStoryの実装が完了していること。'" in errors

        metadata_story = {"labels": ["story"]}
        errors_story = service.validate_plan_content(content, metadata_story)
        assert "Story completion criteria must contain 'このStoryを構成する全てのTaskの実装が完了していること。'" in errors_story
