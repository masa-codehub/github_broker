import os
import json
import textwrap
import google.generativeai as genai

class GeminiClient:
    """
    A client to interact with the Google Gemini API for selecting the best issue.
    """

    def __init__(self):
        """
        Initializes the GeminiClient, configures the API key, and sets up the model.
        Raises:
            ValueError: If the GEMINI_API_KEY environment variable is not set.
        """
        self._api_key = os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError("Gemini API key not found in GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel('gemini-pro')

    def select_best_issue_id(self, issues: list[dict], capabilities: list[str]) -> int | None:
        """
        Selects the best issue ID from a list based on agent capabilities using the Gemini API.

        Args:
            issues (list[dict]): A list of dictionaries, where each dictionary represents an issue.
            capabilities (list[str]): A list of strings representing the agent's capabilities.

        Returns:
            int or None: The ID of the selected issue, or None if no suitable issue is found.
        """
        if not issues:
            return None

        prompt = self._build_prompt(issues, capabilities)

        try:
            response = self._model.generate_content(prompt)
            # Assuming the response.text contains a JSON string like '{"issue_id": 123}'
            response_json = json.loads(response.text)
            return int(response_json.get("issue_id"))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response text: {response.text if 'response' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while calling Gemini API: {e}")
            return None

    def _build_prompt(self, issues: list[dict], capabilities: list[str]) -> str:
        """
        Builds the prompt to be sent to the Gemini API.
        """
        issues_str = "\n".join([f"- ID: {i['id']}, Title: {i['title']}, Body: {i['body']}, Labels: {i['labels']}" for i in issues])
        capabilities_str = ", ".join(capabilities)

        prompt = f"""
        You are an expert software development project manager. Your task is to choose the most suitable issue for a developer agent to work on next.

        Here are the available issues:
        {issues_str}

        Here are the capabilities of the developer agent:
        {capabilities_str}

        Based on the agent's capabilities and the information for each issue (title, body, labels), which issue is the most appropriate for the agent to tackle? 
        Please consider the technical skills required, the context of the issue, and the agent's stated capabilities.

        Respond with ONLY a JSON object in the format: {{"issue_id": <id>}}, where <id> is the integer ID of the chosen issue. Do not include any other text, explanation, or markdown formatting.
        If no issue is suitable, respond with {{"issue_id": null}}.
        """
        return textwrap.dedent(prompt)
