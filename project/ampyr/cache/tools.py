from ampyr import errors, protocols as pt, typedefs as td

DEFAULT_CACHE_PATH = ".cache"
"""
Default filename used for local cache files.
"""


def get_cache_path(path: td.OptFilePath = None,
    *ids: str | None) -> td.FilePath:
    """
    Retrieve the path for some cache file used
    for long-term storage.
    """

    if not path:
        path = DEFAULT_CACHE_PATH

    # Filter out any undefined or null values.
    # Join the remaining to the filepath.
    ids = tuple(filter(lambda i: i != None, ids))
    if len(ids):
        path = "-".join([str(path), *ids]) #type: ignore[list-item]

    return path


def get_generic_key(obj: pt.HasCacheHandler, *ids):
    """
    Constructs a string that can be used as a
    search key for any relevant cache data.
    """

    typename, baseids = type(obj).__name__, []

    for i in ids:
        if hasattr(i, "__name__"):
            baseids.append(i.__name__)
            continue
        baseids.append("('{}')".format(i))

    return "<{}={}>".format(typename, "-".join(baseids))


def build_keypair(join_char: str, key: str, data: str):
    """
    Renders the concatenation of some search key
    and the data related to it.
    """

    return join_char.join([key, data])


def split_keypair(join_char: str, keypair: str):
    """
    From the given `join_char`, divide a
    `keypair` string into its individual
    components.
    """

    return keypair.split(join_char, maxsplit=1)
