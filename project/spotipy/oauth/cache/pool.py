import typing

from spotipy.oauth.cache import base


class SpotifyCachePool:

    _pool:        set[base.SpotifyCacheHandler]
    _handler_cls: type[base.SpotifyCacheHandler]

    _hargs: set[tuple[int, typing.Any]]
    _hkwds: dict[str, typing.Any]

    def __init__(self,
        handler_cls: type[base.SpotifyCacheHandler] = None, *,
        hargs: tuple = None,
        hkwds: dict[str, typing.Any] = None) -> None:

        self._pool = set()

        # Apply default cache handler
        # if none given.
        if not handler_cls:
            handler_cls = base.MemoryCacheHandler
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

    def delete(self, handler: base.SpotifyCacheHandler = None):
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
