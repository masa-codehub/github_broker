from pathlib import Path

import pytest

from github_broker.domain.agent_config import AgentConfigList
from github_broker.infrastructure.agent.loader import AgentConfigLoader


@pytest.fixture
def valid_toml_content() -> str:
    return """
    [[agents]]
    role = "BACKEND_CODER"
    persona = "You are an expert backend coder..."

    [[agents]]
    role = "FRONTEND_CODER"
    persona = "You are a skilled frontend developer..."
    """


@pytest.fixture
def invalid_toml_content() -> str:
    return "this is not valid toml"


@pytest.fixture
def temp_toml_file(tmp_path: Path, valid_toml_content: str) -> Path:
    file_path = tmp_path / "agents.toml"
    file_path.write_text(valid_toml_content)
    return file_path


def test_load_from_file_success(temp_toml_file: Path):
    # Act
    config_list = AgentConfigLoader.load_from_file(temp_toml_file)

    # Assert
    assert isinstance(config_list, AgentConfigList)
    assert len(config_list.agents) == 2
    assert config_list.agents[0].role == "BACKEND_CODER"
    assert config_list.agents[1].persona.startswith("You are a skilled")


def test_load_from_file_not_found():
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        AgentConfigLoader.load_from_file("non_existent_file.toml")


def test_load_from_dict_success():
    # Arrange
    data = {
        "agents": [
            {"role": "TESTER", "persona": "You are a diligent tester."},
            {"role": "DESIGNER", "persona": "You have a keen eye for design."},
        ]
    }

    # Act
    config_list = AgentConfigLoader.load_from_dict(data)

    # Assert
    assert isinstance(config_list, AgentConfigList)
    assert len(config_list.agents) == 2
    assert config_list.find_by_role("TESTER").persona == "You are a diligent tester."
    assert config_list.find_by_role("DESIGNER") is not None
    assert config_list.find_by_role("NON_EXISTENT") is None
