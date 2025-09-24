"""
アプリケーション固有の例外。
"""


class LockAcquisitionError(Exception):
    """タスクのロック取得に失敗した場合に発生します。"""

    pass


class PromptExecutionError(Exception):
    """プロンプトの実行に失敗した場合に発生します。"""

    pass
