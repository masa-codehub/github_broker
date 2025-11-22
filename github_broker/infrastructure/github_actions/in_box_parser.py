import logging
import re

import yaml  # Import PyYAML

logger = logging.getLogger(__name__)

class InboxParser:
    def __init__(self):
        pass

    def parse_issue_file(self, file_content: str) -> dict:
        title = ""
        body = ""
        labels = []
        assignees = []

        front_matter = None
        content_without_front_matter = file_content

        # Check for YAML front matter
        if file_content.startswith("---"):
            parts = file_content.split("---", 2)
            # len(parts) must be 3: ['', front_matter_str, content_str]
            # parts[0] must be empty, meaning no text before the first '---'
            if len(parts) == 3 and not parts[0].strip():
                try:
                    front_matter = yaml.safe_load(parts[1])
                    content_without_front_matter = parts[2].strip()
                except yaml.YAMLError as e:
                    logger.warning(f"Error parsing YAML front matter: {e}")
                    # Continue with the whole file content as body if YAML is invalid
                    front_matter = None
                    content_without_front_matter = file_content
            else:
                # If the structure is not valid, treat the entire content as the body
                content_without_front_matter = file_content

        if front_matter:
            labels = front_matter.get("labels", [])
            assignees = front_matter.get("assignees", [])

        # Extract title (first H1) from content after front matter
        title_match = re.search(r"^#\s*(.*)", content_without_front_matter, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove title from body
            body = re.sub(r"^#\s*.*", "", content_without_front_matter, count=1, flags=re.MULTILINE).strip()
        else:
            body = content_without_front_matter.strip() # If no H1, entire content is body

        return {
            "title": title,
            "body": body,
            "labels": labels,
            "assignees": assignees
        }

