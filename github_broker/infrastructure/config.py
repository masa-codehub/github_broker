from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_PATH), extra="ignore")

    github_app_id: str = Field(..., validation_alias="GITHUB_APP_ID")
    github_app_private_key: str = Field(..., validation_alias="GITHUB_APP_PRIVATE_KEY")
    github_personal_access_token: str = Field(
        ..., validation_alias="GITHUB_PERSONAL_ACCESS_TOKEN"
    )
    github_webhook_secret: str = Field(..., validation_alias="GITHUB_WEBHOOK_SECRET")
    redis_url: str = Field("redis://localhost:6379", validation_alias="REDIS_URL")
    google_api_key: str = Field(..., validation_alias="GOOGLE_API_KEY")
    github_agent_repository: str = Field(
        "gemini-code-assist/gemini-code-assist",
        validation_alias="GITHUB_AGENT_REPOSITORY",
    )
    github_agent_doc_path: str = Field(
        ".gemini/agents", validation_alias="GITHUB_AGENT_DOC_PATH"
    )
    github_agent_doc_branch: str = Field(
        "main", validation_alias="GITHUB_AGENT_DOC_BRANCH"
    )
    github_agent_model_name: str = Field(
        "gemini-1.5-pro-latest", validation_alias="GITHUB_AGENT_MODEL_NAME"
    )
    github_agent_timeout_seconds: int = Field(
        900, validation_alias="GITHUB_AGENT_TIMEOUT_SECONDS"
    )
    github_agent_max_retries: int = Field(
        3, validation_alias="GITHUB_AGENT_MAX_RETRIES"
    )
    github_agent_max_iterations: int = Field(
        25, validation_alias="GITHUB_AGENT_MAX_ITERATIONS"
    )
    github_agent_log_file: str = Field(
        "gemini-agent.log", validation_alias="GITHUB_AGENT_LOG_FILE"
    )
    github_agent_log_level: str = Field(
        "INFO", validation_alias="GITHUB_AGENT_LOG_LEVEL"
    )
    github_agent_log_dir: str = Field(
        "/tmp/gemini-agent", validation_alias="GITHUB_AGENT_LOG_DIR"
    )
    github_agent_output_dir: str = Field(
        "/tmp/gemini-agent/output", validation_alias="GITHUB_AGENT_OUTPUT_DIR"
    )
    github_agent_context_dir: str = Field(
        "/tmp/gemini-agent/context", validation_alias="GITHUB_AGENT_CONTEXT_DIR"
    )
    github_agent_tools_dir: str = Field(
        "/app/tools", validation_alias="GITHUB_AGENT_TOOLS_DIR"
    )
    github_agent_tool_schema_file: str = Field(
        "tool_schema.json", validation_alias="GITHUB_AGENT_TOOL_SCHEMA_FILE"
    )
    github_agent_tool_code_file: str = Field(
        "tool_code.py", validation_alias="GITHUB_AGENT_TOOL_CODE_FILE"
    )
    github_agent_tool_code_template_file: str = Field(
        "tool_code_template.py.j2",
        validation_alias="GITHUB_AGENT_TOOL_CODE_TEMPLATE_FILE",
    )
    github_agent_tool_schema_template_file: str = Field(
        "tool_schema_template.json.j2",
        validation_alias="GITHUB_AGENT_TOOL_SCHEMA_TEMPLATE_FILE",
    )
    github_agent_prompt_template_file: str = Field(
        "prompt_template.md.j2", validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_FILE"
    )
    github_agent_prompt_template_dir: str = Field(
        "/app/prompts", validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_DIR"
    )
    github_agent_prompt_template_context_file: str = Field(
        "context.json", validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_CONTEXT_FILE"
    )
    github_agent_prompt_template_context_dir: str = Field(
        "/app/prompts/context",
        validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_CONTEXT_DIR",
    )
    github_agent_prompt_template_context_schema_file: str = Field(
        "context_schema.json",
        validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_CONTEXT_SCHEMA_FILE",
    )
    github_agent_prompt_template_context_schema_dir: str = Field(
        "/app/prompts/context",
        validation_alias="GITHUB_AGENT_PROMPT_TEMPLATE_CONTEXT_SCHEMA_DIR",
    )


def get_settings() -> Settings:
    return Settings()  # type: ignore
