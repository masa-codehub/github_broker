

import yaml


class IssueData:
    def __init__(self, title: str, body: str, labels: list[str] | None = None, assignees: list[str] | None = None):
        self.title = title
        self.body = body
        self.labels = labels if labels is not None else []
        self.assignees = assignees if assignees is not None else []

def parse_issue_content(content: str) -> IssueData | None:
    """
    Parses the content of a file to extract issue data (title, body, labels, assignees).
    Expected format: YAML Front Matter followed by markdown body.
    """
    parts = content.split('---', 2) # Split into at most 3 parts: before first ---, front matter, body

    if len(parts) < 3: # Not enough parts for YAML Front Matter
        return None

    # First part is empty, second part is YAML Front Matter
    front_matter_str = parts[1].strip()
    body = parts[2].strip()

    try:
        metadata = yaml.safe_load(front_matter_str)
    except yaml.YAMLError:
        return None

    if not isinstance(metadata, dict):
        return None

    title = metadata.get('title')
    labels = metadata.get('labels', [])
    assignees = metadata.get('assignees', [])

    if not isinstance(title, str):
        return None

    if isinstance(labels, list):
        labels = [label for label in labels if isinstance(label, str)]
    else:
        labels = []

    if isinstance(assignees, list):
        assignees = [assignee for assignee in assignees if isinstance(assignee, str)]
    else:
        assignees = []

    return IssueData(title=title, body=body, labels=labels, assignees=assignees)
