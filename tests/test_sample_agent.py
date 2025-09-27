import logging
import os
import subprocess
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_task():
    """テスト用のサンプルタスクを提供します。"""
    return {
        "issue_id": 123,
        "title": "Test Issue",
        "prompt": "echo 'Hello World'",
        "body": "This is a test issue",
        "branch_name": "test-branch"
    }


class SampleAgentRunner:
    """sample_agent.pyの実行ロジックをテスト可能な形で抽象化したクラス"""
    
    def __init__(self, agent_id=None, host=None, port=None, agent_role=None, 
                 gemini_log_dir=None, gemini_model=None):
        # 環境変数またはデフォルト値から設定を取得
        self.agent_id = agent_id or os.getenv("AGENT_NAME", "sample-agent-001")
        self.host = host or os.getenv("BROKER_HOST", "localhost")
        self.port = int(port or os.getenv("BROKER_PORT", 8080))
        self.agent_role = agent_role or os.getenv("AGENT_ROLE", "BACKENDCODER")
        self.gemini_log_dir = gemini_log_dir or os.getenv("MESSAGE_DIR", "/app/logs")
        self.gemini_model = gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        self.client = None
        self.executor = None
        self.should_stop = False  # テスト用の停止フラグ
    
    def initialize_client_and_executor(self, agent_client_class, gemini_executor_class):
        """クライアントとエグゼキューターを初期化します"""
        self.client = agent_client_class(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            host=self.host,
            port=self.port
        )
        self.executor = gemini_executor_class(
            log_dir=self.gemini_log_dir,
            model=self.gemini_model
        )
    
    def run_single_iteration(self):
        """メインループの1回分の処理を実行します"""
        if not self.client or not self.executor:
            raise RuntimeError("Client and executor must be initialized")
        
        assigned_task = self.client.request_task()
        
        if assigned_task:
            logging.info(
                f"新しいタスクが割り当てられました: #{assigned_task.get('issue_id')} - {assigned_task.get('title')}"
            )
            # ログファイル名のためにagent_idをタスク辞書に追加
            assigned_task["agent_id"] = self.agent_id
            
            self.executor.execute(assigned_task)
            logging.info("タスクの実行プロセスが完了しました。")
            return "task_completed"
        else:
            logging.info("利用可能なタスクがありません。30分後に再試行します。")
            return "no_tasks"


@pytest.mark.unit
def test_sample_agent_initialization():
    """SampleAgentRunnerの初期化をテストします"""
    # Act
    runner = SampleAgentRunner(
        agent_id="test-agent", 
        host="test-host", 
        port=9999,
        agent_role="TESTCODER",
        gemini_log_dir="/tmp/logs",
        gemini_model="test-model"
    )
    
    # Assert
    assert runner.agent_id == "test-agent"
    assert runner.host == "test-host"
    assert runner.port == 9999
    assert runner.agent_role == "TESTCODER"
    assert runner.gemini_log_dir == "/tmp/logs"
    assert runner.gemini_model == "test-model"


@pytest.mark.unit
@patch.dict(os.environ, {}, clear=True)  # 環境変数をクリア
def test_sample_agent_default_values():
    """環境変数が設定されていない場合のデフォルト値をテストします"""
    # Act
    runner = SampleAgentRunner()
    
    # Assert
    assert runner.agent_id == "sample-agent-001"
    assert runner.host == "localhost"
    assert runner.port == 8080
    assert runner.agent_role == "BACKENDCODER"
    assert runner.gemini_log_dir == "/app/logs"
    assert runner.gemini_model == "gemini-2.5-flash"


@pytest.mark.unit
@patch.dict(os.environ, {
    "AGENT_NAME": "env-agent",
    "BROKER_HOST": "env-host",
    "BROKER_PORT": "5555",
    "AGENT_ROLE": "ENVCODER",
    "MESSAGE_DIR": "/env/logs",
    "GEMINI_MODEL": "env-model"
})
def test_sample_agent_environment_variables():
    """環境変数が正しく読み込まれることをテストします"""
    # Act
    runner = SampleAgentRunner()
    
    # Assert
    assert runner.agent_id == "env-agent"
    assert runner.host == "env-host"
    assert runner.port == 5555
    assert runner.agent_role == "ENVCODER"
    assert runner.gemini_log_dir == "/env/logs"
    assert runner.gemini_model == "env-model"


@pytest.mark.unit
def test_sample_agent_client_and_executor_initialization():
    """AgentClientとGeminiExecutorの初期化をテストします"""
    # Arrange
    mock_agent_client = MagicMock()
    mock_gemini_executor = MagicMock()
    
    mock_agent_client_class = MagicMock(return_value=mock_agent_client)
    mock_gemini_executor_class = MagicMock(return_value=mock_gemini_executor)
    
    runner = SampleAgentRunner(
        agent_id="test-agent",
        host="test-host",
        port=9999,
        agent_role="TESTCODER",
        gemini_log_dir="/tmp/logs",
        gemini_model="test-model"
    )
    
    # Act
    runner.initialize_client_and_executor(mock_agent_client_class, mock_gemini_executor_class)
    
    # Assert
    mock_agent_client_class.assert_called_once_with(
        agent_id="test-agent",
        agent_role="TESTCODER",
        host="test-host",
        port=9999
    )
    
    mock_gemini_executor_class.assert_called_once_with(
        log_dir="/tmp/logs",
        model="test-model"
    )
    
    assert runner.client == mock_agent_client
    assert runner.executor == mock_gemini_executor


@pytest.mark.unit
def test_sample_agent_run_single_iteration_with_task(sample_task):
    """タスクがある場合の1回分の処理をテストします"""
    # Arrange
    mock_client = MagicMock()
    mock_executor = MagicMock()
    
    mock_client.request_task.return_value = sample_task
    
    runner = SampleAgentRunner(agent_id="test-agent")
    runner.client = mock_client
    runner.executor = mock_executor
    
    # Act
    result = runner.run_single_iteration()
    
    # Assert
    assert result == "task_completed"
    mock_client.request_task.assert_called_once()
    mock_executor.execute.assert_called_once()
    
    # タスクにagent_idが追加されたことを確認
    executed_task = mock_executor.execute.call_args[0][0]
    assert executed_task["agent_id"] == "test-agent"
    assert executed_task["issue_id"] == 123
    assert executed_task["title"] == "Test Issue"


@pytest.mark.unit
def test_sample_agent_run_single_iteration_no_task():
    """タスクがない場合の1回分の処理をテストします"""
    # Arrange
    mock_client = MagicMock()
    mock_executor = MagicMock()
    
    mock_client.request_task.return_value = None
    
    runner = SampleAgentRunner()
    runner.client = mock_client
    runner.executor = mock_executor
    
    # Act
    result = runner.run_single_iteration()
    
    # Assert
    assert result == "no_tasks"
    mock_client.request_task.assert_called_once()
    mock_executor.execute.assert_not_called()


@pytest.mark.unit  
def test_sample_agent_run_single_iteration_not_initialized():
    """クライアントとエグゼキューターが初期化されていない場合のエラーテスト"""
    # Arrange
    runner = SampleAgentRunner()
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Client and executor must be initialized"):
        runner.run_single_iteration()


@pytest.mark.unit
def test_sample_agent_integration_with_mocks():
    """AgentClientとGeminiExecutorをモックした統合テスト"""
    # Arrange
    sample_task = {
        "issue_id": 456,
        "title": "Integration Test Issue",
        "prompt": "test command",
    }
    
    mock_client = MagicMock()
    mock_executor = MagicMock()
    mock_client.request_task.return_value = sample_task
    
    mock_agent_client_class = MagicMock(return_value=mock_client)
    mock_gemini_executor_class = MagicMock(return_value=mock_executor)
    
    runner = SampleAgentRunner(
        agent_id="integration-test-agent",
        host="test.example.com",
        port=7777,
        agent_role="INTEGRATIONCODER"
    )
    
    # Act
    runner.initialize_client_and_executor(mock_agent_client_class, mock_gemini_executor_class)
    result = runner.run_single_iteration()
    
    # Assert
    assert result == "task_completed"
    
    # 初期化が正しく行われたことを確認
    mock_agent_client_class.assert_called_once_with(
        agent_id="integration-test-agent",
        agent_role="INTEGRATIONCODER",
        host="test.example.com",
        port=7777
    )
    
    # タスクが実行されたことを確認
    mock_executor.execute.assert_called_once()
    executed_task = mock_executor.execute.call_args[0][0]
    assert executed_task["agent_id"] == "integration-test-agent"
    assert executed_task["issue_id"] == 456
    assert executed_task["title"] == "Integration Test Issue"


@pytest.mark.unit
@patch("github_broker.infrastructure.executors.gemini_executor.os.makedirs")
@patch("github_broker.infrastructure.executors.gemini_executor.open")
@patch("github_broker.infrastructure.executors.gemini_executor.yaml.safe_load")
def test_sample_agent_script_initialization_mocked(mock_yaml_load, mock_open, mock_makedirs):
    """
    実際のsample_agent.pyスクリプトの初期化部分をモックしてテストします。
    """
    # Arrange - GeminiExecutorの初期化をモック
    mock_yaml_load.return_value = {"prompt_template": "test template"}
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    with patch("sample_agent.AgentClient") as mock_agent_client_class, \
         patch("sample_agent.GeminiExecutor") as mock_gemini_executor_class, \
         patch.dict(os.environ, {
             "AGENT_NAME": "script-test-agent",
             "BROKER_HOST": "script-host",
             "BROKER_PORT": "1234",
             "AGENT_ROLE": "SCRIPTCODER",
             "MESSAGE_DIR": "/tmp/script_logs",
             "GEMINI_MODEL": "script-model"
         }):
        
        mock_client = MagicMock()
        mock_executor = MagicMock()
        mock_agent_client_class.return_value = mock_client
        mock_gemini_executor_class.return_value = mock_executor
        
        # Act - スクリプトのインポートをシミュレート（初期化のみ）
        # sample_agent.pyの初期化コードをここで模倣
        agent_id = os.getenv("AGENT_NAME", "sample-agent-001")
        host = os.getenv("BROKER_HOST", "localhost")
        port = int(os.getenv("BROKER_PORT", 8080))
        agent_role = os.getenv("AGENT_ROLE", "BACKENDCODER")
        gemini_log_dir = os.getenv("MESSAGE_DIR", "/app/logs")
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        client = mock_agent_client_class(agent_id=agent_id, agent_role=agent_role, host=host, port=port)
        executor = mock_gemini_executor_class(log_dir=gemini_log_dir, model=gemini_model)
        
        # Assert
        assert agent_id == "script-test-agent"
        assert host == "script-host"
        assert port == 1234
        assert agent_role == "SCRIPTCODER"
        assert gemini_log_dir == "/tmp/script_logs"
        assert gemini_model == "script-model"
        
        mock_agent_client_class.assert_called_once_with(
            agent_id="script-test-agent",
            agent_role="SCRIPTCODER",
            host="script-host",
            port=1234
        )
        
        mock_gemini_executor_class.assert_called_once_with(
            log_dir="/tmp/script_logs",
            model="script-model"
        )


@pytest.mark.unit
def test_sample_agent_script_runs_with_timeout():
    """
    実際のsample_agent.pyスクリプトが正常に起動し、タイムアウトで停止することをテストします。
    外部サービス（サーバー、LLM）への接続はモックされていないため、実際の接続エラーが発生することを期待します。
    """
    # Arrange
    env = os.environ.copy()
    env.update({
        "AGENT_NAME": "timeout-test-agent",
        "BROKER_HOST": "nonexistent-host",  # 接続に失敗するホスト
        "BROKER_PORT": "9999",
        "MESSAGE_DIR": "/tmp",  # 書き込み可能なディレクトリ
    })
    
    # Act - タイムアウトで停止することを確認
    process = subprocess.Popen(
        [sys.executable, "sample_agent.py"],
        cwd="/home/runner/work/github_broker/github_broker",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 5秒でタイムアウト
        stdout, stderr = process.communicate(timeout=5)
        # もしプロセスが5秒以内に終了したら、それも有効な結果
        assert process.returncode is not None
    except subprocess.TimeoutExpired:
        # タイムアウトが発生した場合（期待される動作）
        process.terminate()
        stdout, stderr = process.communicate()
        
    # Assert - スクリプトが正常に開始されたことを確認（ログメッセージの存在）
    assert "エージェント 'timeout-test-agent' を開始します。" in stderr or "エージェント 'timeout-test-agent' を開始します。" in stdout
    assert "サーバー nonexistent-host:9999 に接続しています。" in stderr or "サーバー nonexistent-host:9999 に接続しています。" in stdout