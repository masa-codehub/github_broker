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
            # パターンA: `- **作業ブランチ (Feature Branch):** ([^\s`]+)`
            #   - `- **作業ブランチ (Feature Branch):**`: リテラル文字列
            #   - `([^\s`]+)`: 空白とバッククォート以外の1文字以上にマッチ（キャプチャグループ1）
            # パターンB: `## ブランチ名(?: \(Branch name\))?\s*`?([^\s`]+)`?`
            #   - `## ブランチ名`: リテラル文字列
            #   - `(?: \(Branch name\))?`: オプションの英語注釈
            #   - `\s*`?`: 空白文字
            #   - ``?`: オプションのバッククォート
            #   - `([^\s`]+)`: 空白とバッククォート以外の1文字以上にマッチ（キャプチャグループ2）
            pattern = r"- \*\*作業ブランチ \(Feature Branch\):\*\* `?([^\s`]+)`?|## ブランチ名(?: \(Branch name\))?\s*`?([^\s`]+)`?"
            match = re.search(
                pattern,
                self.body,
                re.MULTILINE,
            )

            if match:
                # グループ1（パターンA）またはグループ2（パターンB）にマッチした方を取得
                branch_name = (match.group(1) or match.group(2)).strip()
                return branch_name.replace("issue-xx", f"issue-{self.issue_id}")
        return None
