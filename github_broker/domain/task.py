import re
from dataclasses import dataclass
from enum import Enum


class TaskCandidateStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"


@dataclass
class Task:
    issue_id: int
    title: str
    body: str
    html_url: str
    labels: list[str]

    def is_assignable(self) -> bool:
        """Issueの本文に「## 成果物」セクションが存在するかどうかを判定します。"""
        if self.body:
            return bool(re.search(r"^## 成果物", self.body, re.MULTILINE))
        return False

    def extract_branch_name(self) -> str | None:
        """Issueの本文からブランチ名を抽出します。"""
        if self.body:
            # 正規表現パターン:
            # `## ブランチ名`: リテラル文字列 "## ブランチ名" にマッチ
            # `(?: \(Branch name\))?`: オプションの非キャプチャグループで、"(Branch name)" にマッチ (英語の注釈に対応)
            # `\s*`: 0個以上の空白文字にマッチ
            # ``?`: オプションのバッククォートにマッチ
            # `([^\s`]+)`: 1個以上の空白文字またはバッククォート以外の文字にマッチし、これをキャプチャグループ1とする (ブランチ名本体)
            # ``?`: オプションのバッククォォートにマッチ
            match = re.search(
                r"## ブランチ名(?: \(Branch name\))?\s*`?([^\s`]+)`?",
                self.body,
                re.MULTILINE,
            )
            if match:
                branch_name = match.group(1).strip()
                return branch_name.replace("issue-xx", f"issue-{self.issue_id}")
        return None
