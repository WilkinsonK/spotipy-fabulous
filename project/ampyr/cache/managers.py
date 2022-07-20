"""
General purpose `CacheManager` objects. Use these
classes as handlers for brokering data to/from
some cache.
"""

from ampyr import factories as ft, protocols as pt, typedefs as td


class NullCacheManager(pt.CacheManager[type[None]]):
    """
    Cache manager which strictly returns `None`.
    Used as a dummy value.
    """

    def find(self, key: str):
        return None

    def save(self, key: str, data: td.GT):
        return data


class MemoryCacheManager(pt.CacheManager[td.GT]):
    """
    Cache manager which stores it's inputs in
    memory during runtime.
    """

    stored_data: dict[str, td.GT] = dict()

    def find(self, key: str):
        return self.stored_data.get(key, None)

    def save(self, key: str, data: td.GT):
        self.stored_data[key] = data
        return data
