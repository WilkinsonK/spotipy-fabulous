import json, os, shelve, types

import redis
import django.http.request as djreq

from spotipy import oauth
from spotipy.oauth.cache import base


# Used in the event no initial path is passed
# to `make_cache_path`. This ensures the file
# path is never empty.
DEFAULT_CACHE_PATH = ".cache"


def make_cache_path(path: os.PathLike = None, *ids: str) -> str:
    """
    Generate a path for some cache file.
    """

    if not path:
        path = DEFAULT_CACHE_PATH

    # Filter out any undefined or null
    # values. Join the remaining to
    # the filepath.
    ids = [idx for idx in ids if idx]
    if len(ids):
        path = "-".join([path, *ids])

    return path


class MemoryCacheHandler(base.BaseCacheHandler):
    """
    Stores token data in memory at runtime
    simply as a dictionary.
    """

    _token_data: oauth.TokenData

    def __init__(self, token_data: oauth.TokenData = None):
        self._token_data = token_data

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        self._token_data = token_data

    def find_token_data(self) -> oauth.TokenData | None:
        return self._token_data


# Requires json module.
class FileCacheHandler(base.BaseCacheHandler):
    """
    Stores token data on disk as a
    `JSON` file location.
    """

    _path: str

    def __init__(self, path: os.PathLike = None, *, user_id: str = None):
        self._path = make_cache_path(path, user_id)

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        with open(self._path, "w") as fd:
            fd.write(json.dumps(token_data))

    def find_token_data(self) -> oauth.TokenData | None:
        # Avoid catastrophie and
        # skip if no file found.
        if not os.path.exists(self._path):
            return

        with open(self._path, "r") as fd:
            return json.loads(fd.read())


# Requires shelve module.
class ShelfCacheHandler(FileCacheHandler):
    """
    Utilizes a simple database interaction
    creating `shelves`.
    """

    _search_key: str | None

    def __init__(self, path: os.PathLike = None, *,
        user_id: str = None,
        search_key: str = None):

        super(ShelfCacheHandler, self).__init__(path, user_id=user_id)

        self._search_key = search_key or "token_data"

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        with shelve.open(self._path) as db:
            db[self._search_key] = token_data

    def find_token_data(self) -> oauth.TokenData | None:
        if not os.path.exists(self._path):
            return

        with shelve.open(self._path) as db:
            return db[self._search_key]


# Requires redis and json modules.
class RedisCacheHandler(base.BaseCacheHandler):
    """
    Utilizes a `Redis` instance to store
    token data.
    """

    _redis:      redis.Redis
    _search_key: str | None
    _serializer: types.ModuleType

    def __init__(self, conn: redis.Redis, *, search_key: str = None):
        self._redis      = conn
        self._search_key = search_key or "token_data"

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        dump = json.dumps(token_data)
        self._redis.set(self._search_key, dump)

    def find_token_data(self) -> oauth.TokenData | None:
        dump = self._redis.get(self._search_key)
        return json.loads(dump)


class DjangoCacheHandler(base.BaseCacheHandler):
    """
    Stores token data in a Django Session
    object.
    """

    _request: djreq.HttpRequest

    def __init__(self, request: djreq.HttpRequest = None):
        self._request = request

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        # Avoid catastrophie and skip
        # if no request object present.
        if not self._request:
            return
        self._request.session["token_data"] = token_data

    def find_token_data(self) -> oauth.TokenData | None:
        return self._request.session.get("token_data", None)
