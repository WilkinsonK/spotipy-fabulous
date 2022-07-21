"""
Defines behavior of brokering raw data into/from
Python objects.
"""

from ampyr import factories as ft, protocols as pt, typedefs as td


class NullLoader(pt.SupportsSerialize[td.GT]):
    """
    Dummy value which acts as a pass-through
    object when no serializer is required or
    wanted.
    """

    def loads(self, data, *args, **kwds):
        return data

    def dumps(self, data, *args, **kwds):
        return data


def load(serializer: pt.SupportsSerialize[td.GT], data: td.StrOrBytes, *,
    factory: ft.OptGenericFT[td.GT] = None) -> td.GT:
    """
    Loads raw `data` using some `serializer`.

    factory option allows for post-serialization
    manipulation of the data/object.
    """

    if not factory:
        factory = ft.basic_passthrough_ft
    return factory(serializer.loads(data)) #type: ignore[type-var]


def dump(serializer: pt.SupportsSerialize[td.GT], obj: td.GT, *,
    factory: ft.OptGenericFT = None) -> td.StrOrBytes:
    """
    Deconstructs the given `data` into the format
    of the given `serializer`.

    factory option allows for pre-serialization
    deconstruction of the given data/object.
    """

    if not factory:
        factory = ft.basic_passthrough_ft
    return serializer.dumps(factory(obj))
