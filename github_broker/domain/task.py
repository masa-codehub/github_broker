import re
from dataclasses import dataclass


@dataclass
class Task:
    issue_id: int
    title: str
    body: str
    html_url: str
    labels: list[str]

    def is_assignable(self) -> bool:
        # TODO: Issueの準備状態をチェックするロジックをここに移動する
        return True

    def extract_branch_name(self) -> str | None:
        # TODO: ブランチ名を決定するロジックをここに移動する
        if self.body:
            match = re.search(r"## ブランチ名\s*\n\s*`?([^\s`]+)`?", self.body)
            if match:
                branch_name = match.group(1).strip()
                return branch_name.replace("issue-xx", f"issue-{self.issue_id}")
        return None
