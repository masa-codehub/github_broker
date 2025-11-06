from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

# 存在しないが、テスト対象のクラスとモデルをインポート
from github_broker.domain.agent_config import AgentConfig, AgentDefinition
from github_broker.infrastructure.agent.loader import AgentConfigLoader

# --- Fixtures ---

@pytest.fixture
def valid_yaml_content() -> str:
    """有効なエージェント設定YAMLコンテンツを返すフィクスチャ。"""
    return """
agents:
  - role: BACKENDCODER
    description: Backend development and architecture.
    prompt: The system prompt for the backend coder.
  - role: FRONTENDCODER
    description: Frontend development and UI/UX.
    prompt: The system prompt for the frontend coder.
"""

@pytest.fixture
def invalid_yaml_syntax() -> str:
    """構文的に不正なYAMLコンテンツを返すフィクスチャ。"""
    return """
agents:
  - role: BACKENDCODER
    description: Backend development and architecture.
    prompt: The system prompt for the backend coder.
  - role: FRONTENDCODER
    description: Frontend development and UI/UX.
    prompt: The system prompt for the frontend coder.
: invalid_key # コロンが不正な位置にある
"""

@pytest.fixture
def invalid_pydantic_data() -> str:
    """Pydanticの検証に失敗する（必須フィールド欠落）YAMLコンテンツを返すフィクスチャ。"""
    return """
agents:
  - description: Backend development and architecture.
    prompt: The system prompt for the backend coder.
  - role: FRONTENDCODER
    description: Frontend development and UI/UX.
    prompt: The system prompt for the frontend coder.
"""

@pytest.fixture
def create_temp_yaml_file(tmp_path: Path):
    """一時ディレクトリにYAMLファイルを作成し、そのパスを返すファクトリフィクスチャ。"""
    def _create_temp_yaml_file(content: str) -> Path:
        d = tmp_path / "config"
        d.mkdir(exist_ok=True)
        p = d / "agents.yml"
        p.write_text(content, encoding="utf-8")
        return p
    return _create_temp_yaml_file

# --- Tests ---

def test_load_config_success(create_temp_yaml_file, valid_yaml_content: str):
    """有効なYAMLファイルを正常に読み込み、AgentConfigオブジェクトを返すことを検証する。"""
    yaml_path = create_temp_yaml_file(valid_yaml_content)

    loader = AgentConfigLoader(config_path=yaml_path)
    result = loader.load_config()

    assert isinstance(result, AgentConfig)

    # AgentConfigオブジェクトのagents属性を検証
    agents = result.agents
    assert isinstance(agents, list)
    assert len(agents) == 2
    assert all(isinstance(item, AgentDefinition) for item in agents)

    assert agents[0].role == "BACKENDCODER"
    assert agents[1].role == "FRONTENDCODER"
    assert agents[0].prompt == "The system prompt for the backend coder."


def test_load_config_file_not_found():
    """ファイルが存在しない場合にFileNotFoundErrorをスローすることを検証する。"""
    non_existent_path = Path("/non/existent/path/agents.yml")
    loader = AgentConfigLoader(config_path=non_existent_path)

    with pytest.raises(FileNotFoundError):
        loader.load_config()


def test_load_config_invalid_yaml_syntax(create_temp_yaml_file, invalid_yaml_syntax: str):
    """不正なYAML構文の場合にyaml.YAMLErrorをスローすることを検証する。"""
    yaml_path = create_temp_yaml_file(invalid_yaml_syntax)

    loader = AgentConfigLoader(config_path=yaml_path)

    with pytest.raises(yaml.YAMLError):
        loader.load_config()


def test_load_config_pydantic_validation_error(create_temp_yaml_file, invalid_pydantic_data: str):
    """Pydanticの検証に失敗した場合にValidationErrorをスローすることを検証する。"""
    yaml_path = create_temp_yaml_file(invalid_pydantic_data)

    loader = AgentConfigLoader(config_path=yaml_path)

    with pytest.raises(ValidationError):
        loader.load_config()
