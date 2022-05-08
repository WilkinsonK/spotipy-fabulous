import itertools, secrets, sys, typing

import spotipy.oauth.cache as cache


HandlerFactoryType = typing.Callable[[dict], cache.SpotifyCacheHandler]
HandlerFactory     = typing.TypeVar("HandlerFactory", bound=HandlerFactoryType)
"""A function which generates a `SpotifyCacheHandler` instance."""


def parse_param_sets(param_sets: dict[str, typing.Iterable]) -> enumerate[dict]:
    """
    Generate all possible combinations
    of the given paramsets.
    """
    for key, it in param_sets.items():
        param_sets[key] = [(key, i) for i in it]

    temp = []
    for prod in itertools.product(*param_sets.values()):
        temp.append({key:val for key, val in prod})
    return enumerate(temp)


def cache_handler_suite(
    func: HandlerFactory = None, *,
    param_sets: dict[str, typing.Iterable] = None):

    _globals    = globals()
    _param_sets = param_sets or []

    def wrapper(func: HandlerFactory):

        def test(dec: typing.Callable):
            name = dec.__qualname__.replace(".<locals>.", ".")
            name = name.replace(".wrapper.", ".")
            name = "_".join([func.__qualname__, name])

            def inner():
                for idx, ctx in _param_sets:
                    try:
                        dec(ctx)
                    except Exception as error:
                        etype = type(error)
                        raise etype(str(error), ctx)

            _globals[name] = inner

        @test
        def can_instantiate(ctx: dict):
            assert func(ctx) is not None

        @test
        def can_save_data(ctx: dict, error=None):
            handler    = func(ctx)
            token_data = ctx["token_data"]

            handler.save_token_data(token_data)
            assert handler.find_token_data() is token_data

        @test
        def can_find_data(ctx: dict):
            handler    = func(ctx)
            token_data = ctx["token_data"]

            assert handler.find_token_data() in (None, token_data)

            handler.save_token_data(token_data)
            assert handler.find_token_data() is token_data

    if not func:
        return wrapper
    return wrapper(func)


BASIC_PARAMSETS = {
    "string_id": [secrets.token_urlsafe(16) for _ in range(4)] + [None],
    "path": [None, ".test-cache"],
    "token_data": [
        {
            "access_token": secrets.token_urlsafe(16),
            "scope": "",
            "state": ""
        },
        {
            "access_token": secrets.token_urlsafe(16),
            "scope": "user-library-read user-library-write",
            "state": "expired"
        },
        {
            "access_token": secrets.token_urlsafe(16),
            "scope": "user-library-read user-library-write",
            "state": ""
        },
        {
            "access_token": secrets.token_urlsafe(16),
            "scope": "",
            "state": "expired"
        },
        {
            "access_token": None,
            "scope": None,
            "state": None
        }
    ]
}


BASIC_PARAMSETS = parse_param_sets(BASIC_PARAMSETS)


@cache_handler_suite(param_sets=BASIC_PARAMSETS)
def test_memory_handler(ctx: dict):
    return cache.MemoryCacheHandler(ctx["token_data"])


@cache_handler_suite(param_sets=BASIC_PARAMSETS)
def test_file_handler(ctx: dict):
    return cache.FileCacheHandler(ctx["path"], user_id=ctx["string_id"])


@cache_handler_suite(param_sets=BASIC_PARAMSETS)
def test_shelf_handler(ctx: dict):
    return cache.ShelfCacheHandler(ctx["path"], user_id=ctx["string_id"])
