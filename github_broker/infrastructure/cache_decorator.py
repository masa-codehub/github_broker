import asyncio
import functools
import json
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


def cache_result(key_format: str, ttl: int):
    """
    メソッドの結果をRedisにキャッシュするデコレータ。

    注意: このデコレータは、デコレートされた関数をコルーチンに変換します。呼び出し元は `await` を使用する必要があります。

    :param key_format: キャッシュキーのフォーマット文字列。
                       インスタンスの属性やメソッドの引数を波括弧で参照できます
                       (例: "github:repo:{self._repo_name}:pr:{0}")。
    :param ttl: キャッシュの有効期間（秒）。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_redis_client') or not self._redis_client:
                if asyncio.iscoroutinefunction(func):
                    return await func(self, *args, **kwargs)
                return func(self, *args, **kwargs)

            # キーをフォーマット
            try:
                # selfをキーワード引数として、*argsを位置引数として渡すことで、
                # フォーマット文字列から両方を参照できるようにします。
                key = key_format.format(*args, self=self)
            except (IndexError, KeyError) as e:
                logger.warning(f"キャッシュキーのフォーマットに失敗しました: {key_format}, error: {e}")
                # フォーマットに失敗した場合はキャッシュをバイパス
                if asyncio.iscoroutinefunction(func):
                    return await func(self, *args, **kwargs)
                return func(self, *args, **kwargs)

            # キャッシュを確認
            cached_data = await asyncio.to_thread(self._redis_client.get_value, key)
            if cached_data:
                logger.info(f"キャッシュからデータを取得しました: {key}")
                return json.loads(cached_data)

            # キャッシュがない場合は関数を実行
            if asyncio.iscoroutinefunction(func):
                result = await func(self, *args, **kwargs)
            else:
                result = func(self, *args, **kwargs)

            # 結果をキャッシュに保存
            await asyncio.to_thread(self._redis_client.set_value, key, json.dumps(result), timeout=ttl)
            logger.info(f"データをキャッシュに保存しました: {key} (TTL: {ttl}s)")

            return result
        return wrapper
    return decorator
