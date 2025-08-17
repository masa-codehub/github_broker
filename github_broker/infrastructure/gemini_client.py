import json
import logging
import os
import textwrap

import google.generativeai as genai


class GeminiClient:
    """
    最適なIssueを選択するためにGoogle Gemini APIと対話するクライアント。
    """

    def __init__(self):
        """
        GeminiClientを初期化し、APIキーを設定し、モデルをセットアップします。
        Raises:
            ValueError: GEMINI_API_KEY環境変数が設定されていない場合。
        """
        self._api_key = os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Gemini API key not found in GEMINI_API_KEY environment variable."
            )

        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    def select_best_issue_id(
        self, issues: list[dict], capabilities: list[str]
    ) -> int | None:
        """
        Gemini APIを使用して、エージェントの機能に基づいてリストから最適なIssue IDを選択します。
        API呼び出しが失敗した場合、リストの最初のIssueを選択するフォールバックを行います。

        Args:
            issues (list[dict]): 各辞書がIssueを表す辞書のリスト。
            capabilities (list[str]): エージェントの機能を表す文字列のリスト。

        Returns:
            int or None: 選択されたIssueのID、または適切なIssueが見つからない場合はNone。
        """
        if not issues:
            return None

        prompt = self._build_prompt(issues, capabilities)

        try:
            response = self._model.generate_content(prompt)
            response_json = json.loads(response.text)
            issue_id = response_json.get("issue_id")
            if issue_id is None:
                return None
            return int(issue_id)
        except Exception as e:
            logging.warning(
                f"Gemini API call failed: {e}. Falling back to basic selection."
            )
            # 最初のIssueを選択するフォールバック
            return issues[0].get("id")

    def _build_prompt(self, issues: list[dict], capabilities: list[str]) -> str:
        """
        Gemini APIに送信するプロンプトを構築します。
        """
        # 'body'または'labels'が欠落している場合に備えて.get()を使用
        issues_str = "\n".join(
            [
                f"- ID: {i['id']}, Title: {i['title']}, Body: {i.get('body', '')}, Labels: {i.get('labels', [])}"
                for i in issues
            ]
        )
        capabilities_str = ", ".join(capabilities)

        prompt = f"""
        あなたは熟練したソフトウェア開発プロジェクトマネージャーです。あなたのタスクは、開発者エージェントが次に作業するのに最も適したIssueを選択することです。

        利用可能なIssueは以下の通りです:
        {issues_str}

        開発者エージェントの機能は以下の通りです:
        {capabilities_str}

        エージェントの機能と各Issueの情報（タイトル、本文、ラベル）に基づいて、エージェントが取り組むのに最も適切なIssueはどれですか？
        必要な技術スキル、Issueのコンテキスト、およびエージェントの明示された機能を考慮してください。

        {{'issue_id': <id>}}の形式のJSONオブジェクトのみで応答してください。<id>は選択されたIssueの整数IDです。他のテキスト、説明、またはマークダウン形式を含めないでください。
        適切なIssueがない場合は、{{'issue_id': null}}で応答してください。
        """
        return textwrap.dedent(prompt)
