import json
import logging

import google.generativeai as genai


class GeminiClient:
    """
    最適なIssueを選択するためにGoogle Gemini APIと対話するクライアント。
    """

    def __init__(self, gemini_api_key: str):
        self._api_key = gemini_api_key

        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    def select_best_issue_id(self, prompt: str) -> int | None:
        """
        Gemini APIを使用して、エージェントの機能に基づいてリストから最適なIssue IDを選択します。
        API呼び出しが失敗した場合、リストの最初のIssueを選択するフォールバックを行います。

        Args:
            issues (list[dict]): 各辞書がIssueを表す辞書のリスト。
            capabilities (list[str]): エージェントの機能を表す文字列のリスト。

        Returns:
            int or None: 選択されたIssueのID、または適切なIssueが見つからない場合はNone。
        """
        try:
            response = self._model.generate_content(prompt)
            response_json = json.loads(response.text)
            issue_id = response_json.get("issue_id")
            if issue_id is None:
                return None
            return int(issue_id)
        except Exception as e:
            logging.warning(
                f"Gemini API呼び出しが失敗しました: {e}。適切なIssueが見つかりませんでした。"
            )
            return None
