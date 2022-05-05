import abc
import json
import os
import shelve
import types
import typing

import redis
import django.http.request as djreq

import spotipy.oauth.utils as utils


TokenDataType = dict[str, typing.Any]
TokenData     = typing.TypeVar("TokenData", bound=TokenDataType)


class SpotifyCacheHandler(typing.Protocol):

    def save_token_data(self, token_data: TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    def find_token_data(self) -> TokenData | None:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """


class SpotifyCachePool:

    _pool:        set[SpotifyCacheHandler]
    _handler_cls: type[SpotifyCacheHandler]

    _hargs: set[tuple[int, typing.Any]]
    _hkwds: dict[str, typing.Any]

    def __init__(self,
        handler_cls: type[SpotifyCacheHandler] = None, *,
        hargs: tuple = None,
        hkwds: dict[str, typing.Any] = None) -> None:

        self._pool = set()

        # Apply default cache handler
        # if none given.
        if not handler_cls:
            handler_cls = MemoryCacheHandler
        self._handler_cls = handler_cls

        # Apply default handler args
        # and keywords if none provided.
        if not hargs:
            hargs = ()
        if not hkwds:
            hkwds = {}

        self._hkwds = hkwds
        self._hargs = set(enumerate(hargs))

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, etback):
        while len(self._pool):
            self.delete()

    def new(self, *args, **kwds):
        """
        Request a new handler from this
        pool.
        """

        # Filter out duplicate positionals,
        # replacing defaults with given.
        hargs = self._hargs.copy()
        hargs.update(set(enumerate(args)))
        args = [a[1] for a in sorted(hargs, key=lambda o: o[0])]

        # Filter out duplicate keyword
        # arguments, replacing defaults
        # with given.
        kwds.update(self._hkwds)

        inst = self._handler_cls(*args, **kwds)
        self._pool.add(inst)
        return inst

    def delete(self, handler: SpotifyCacheHandler = None):
        """
        Remove a handler from this pool.

        if `handler` is provided, the specified
        is discarded from the pool. Otherwise,
        `pop` is called and that subsequent handler
        is deleted instead.
        """

        # Discards the handler regardless
        # if is in pool or not.
        if not handler:
            handler = self._pool.pop()
        else:
            self._pool.discard(handler)

        del(handler)


class BaseCacheHandler(abc.ABC):

    @abc.abstractmethod
    def save_token_data(self, token_data: TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    @abc.abstractmethod
    def find_token_data(self) -> TokenData | None:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """


class MemoryCacheHandler(BaseCacheHandler):
    """
    Stores token data in memory at runtime
    simply as a dictionary.
    """

    _token_data: TokenData

    def __init__(self, token_data: TokenData = None):
        self._token_data = token_data

    def save_token_data(self, token_data: TokenData) -> None:
        self._token_data = token_data

    def find_token_data(self) -> TokenData | None:
        return self._token_data


# Requires json module.
class FileCacheHandler(BaseCacheHandler):
    """
    Stores token data on disk as a
    `JSON` file location.
    """

    _path: str

    def __init__(self, path: os.PathLike = None, *, user_id: str = None):
        self._path = utils.make_cache_path(path, user_id)

    def save_token_data(self, token_data: TokenData) -> None:
        with open(self._path, "w") as fd:
            fd.write(json.dumps(token_data))

    def find_token_data(self) -> TokenData | None:
        # Avoid catastrophie and
        # skip if no file found.
        if not os.path.exists(self._path):
            return

        with open(self._path, "r") as fd:
            return json.loads(fd.read())


# Requires shelve module.
class ShelfCacheHandler(BaseCacheHandler):
    """
    Utilizes a simple database interaction
    creating `shelves`.
    """


# Requires redis and json modules.
class RedisCacheHandler(BaseCacheHandler):
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

    def save_token_data(self, token_data: TokenData) -> None:
        dump = json.dumps(token_data)
        self._redis.set(self._search_key, dump)

    def find_token_data(self) -> TokenData | None:
        return self._redis.get(self._search_key)


class DjangoCacheHandler(BaseCacheHandler):
    """
    Stores token data in a Django Session
    object.
    """

    _request: djreq.HttpRequest

    def __init__(self, request: djreq.HttpRequest = None):
        self._request = request

    def save_token_data(self, token_data: TokenData) -> None:
        # Avoid catastrophie and skip
        # if no request object present.
        if not self._request:
            return
        self._request.session["token_data"] = token_data

    def find_token_data(self) -> TokenData | None:
        return self._request.session.get("token_data", None)



with SpotifyCachePool(MemoryCacheHandler) as cp:
    x = cp.new()
    x.save_token_data({})
