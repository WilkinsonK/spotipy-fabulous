"""
General purpose `CacheManager` objects. Use these
classes as handlers for brokering data to/from
some cache.
"""

import json, os, shelve

from ampyr import protocols as pt, typedefs as td
from ampyr.cache import loaders, tools


class SimpleCacheManager(pt.CacheManager[td.GT]):
    """
    Defines basic attributes and construction
    of subsequent `CacheManager` objects.

    WARNING: not meant to be used directly!
    """

    serializer: pt.SupportsSerialize[td.GT]
    """
    An object which can transform data to/from a
    raw state (i.e. a string or byte array) and
    Python objects.
    """

    sub_ids: tuple[td.StrOrBytes, ...]
    """
    Series of strings or byte arrays associated
    with this `CacheManager`.
    """

    def __init__(self, *,
        serializer: td.Optional[pt.SupportsSerialize] = None,
        sub_ids: td.Optional[tuple[td.StrOrBytes, ...]] = None):
        """Construct a new `CacheManager`."""

        self.serializer = (
            serializer
            or getattr(self, "serializer", None)
            or loaders.NullLoader())

        self.sub_ids    = sub_ids or ()


class NullCacheManager(SimpleCacheManager[None]):
    """
    Cache manager which strictly returns `None`.
    Used as a dummy value.
    """

    def find(self, key: str):
        return None

    def save(self, key: str, data: td.GT):
        return data


class MemoryCacheManager(SimpleCacheManager[td.GT]):
    """
    Cache manager which stores it's inputs in
    memory during runtime.
    """

    stored_data: dict[str, td.StrOrBytes] = dict()

    def find(self, key: str):
        found = self.stored_data.get(key, None)
        if not found:
            return None
        return loaders.load(self.serializer, found)

    def save(self, key: str, data: td.GT):
        dump = loaders.dump(self.serializer, data)
        self.stored_data[key] = dump
        return data


class LocalDataCacheManager(SimpleCacheManager[td.GT]):
    """Stores data locally on disc."""

    data_location: td.FilePath
    """Path to where data is stored."""

    @property
    def fileexists(self):
        """
        Whether or not the `data_location`
        attribute points to a valid-- existing--
        file.
        """

        path = self.data_location
        return os.path.exists(path) and os.path.isfile(path)


    def __init__(self, *,
        data_location: td.OptFilePath = None,
        serializer: td.Optional[pt.SupportsSerialize] = None,
        sub_ids: td.Optional[tuple[td.StrOrBytes, ...]]= None):

        super().__init__(
            serializer=serializer,
            sub_ids=sub_ids)
        self.data_location = tools.get_cache_path(data_location)


class FileCacheManager(LocalDataCacheManager[td.GT]):
    """
    Stores data on disc locally as a file which
    records some serialized data.

    The intended purpose for this object is to
    serve single record use.
    """

    serializer: pt.SupportsSerialize[td.GT] = json

    join_char: str = ":"
    """
    Character used to join keys to corresponding
    data.
    """

    def find(self, key: str):
        # Avoid catastrophie and skip if no file
        # exists yet.
        if not self.fileexists:
            return None

        with open(self.data_location, "r") as fd:
            fkey, found = tools.split_keypair(self.join_char, fd.read())

            # If the key associated with the file
            # data does not match the given key,
            # bail.
            if fkey != key:
                return None
            return loaders.load(self.serializer, found)

    def save(self, key: str, data: td.GT):
        with open(self.data_location, "w") as fd:
            # Ensures given data is written as a
            # string.
            dump = str(loaders.dump(self.serializer, data))
            fd.write(tools.build_keypair(self.join_char, key, dump))


def _open_shelf(filepath: str) -> shelve.Shelf[td.StrOrBytes]:
    """
    Open's a shelf in context.
    NOTE: Must close manually.
    """

    return shelve.open(filepath) #type: ignore[return-value]


class ShelfCacheManager(LocalDataCacheManager[td.GT]):
    """
    Stores data on disc locally as a series of
    shelves using the `shelve` module.
    """

    # Override this method. `shelve` module
    # creates multiple files for data store.
    @property
    def fileexists(self):
        path = self.data_location

        # If is single file db instance.
        temp_path = ".".join([path, "db"])
        if os.path.exists(temp_path):
            return True

        # shelve module generates multiple files.
        for ext in ("dat", "dir", "bak"):
            temp_path = ".".join([path, ext])

            # If required file doesn't exist,
            # bail.
            if not os.path.exists(temp_path):
                return False

            # If required target is not a file,
            # bail.
            if not os.path.isfile(temp_path):
                return False

        return True

    def find(self, key: str):
        if not self.fileexists:
            return None

        with _open_shelf(str(self.data_location)) as db:
            found = db.get(key, None)
            db.close()

        if not found:
            return None
        return loaders.load(self.serializer, found)

    def save(self, key: str, data: td.GT):
        with _open_shelf(str(self.data_location)) as db:
            db[key] = loaders.dump(self.serializer, data)
            db.close()
        return data
