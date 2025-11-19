import functools
import json
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


def cache_result(key_format: str, ttl: int):
    """
    メソッドの結果をRedisにキャッシュするデコレータ。

    :param key_format: キャッシュキーのフォーマット文字列。
                       インスタンスの属性を波括弧で参照できます (例: "github:repo:{self._repo_name}")。
    :param ttl: キャッシュの有効期間（秒）。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._redis_client:
                return func(self, *args, **kwargs)

            # キーをフォーマット
            try:
                # selfとargs[0] (pull_numberなど) の両方をキーに含められるようにする
                all_args = (self,) + args
                key = key_format.format(*all_args, self=self)
            except (IndexError, KeyError) as e:
                logger.error(f"キャッシュキーのフォーマットに失敗しました: {key_format}, error: {e}")
                # フォーマットに失敗した場合はキャッシュをバイパス
                return func(self, *args, **kwargs)

            # キャッシュを確認
            cached_data = self._redis_client.get_value(key)
            if cached_data:
                logger.info(f"キャッシュからデータを取得しました: {key}")
                return json.loads(cached_data)

            # キャッシュがない場合は関数を実行
            result = func(self, *args, **kwargs)

            # 結果をキャッシュに保存
            self._redis_client.set_value(key, json.dumps(result), timeout=ttl)
            logger.info(f"データをキャッシュに保存しました: {key} (TTL: {ttl}s)")

            return result
        return wrapper
    return decorator
