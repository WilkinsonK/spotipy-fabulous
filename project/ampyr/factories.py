"""
Subcategory for typedefs to outline factories
used in this package.
"""

import functools
from typing import Any, Callable, Optional

import requests

from ampyr import  protocols as pt, typedefs as td

InstanceFT = Callable[[type[td.GT]], td.GT]
"""
A generic factory which constructs an instance of
the given type.
"""

OptInstanceFT = Optional[InstanceFT]
"""Optional `InstanceFactory`."""


def basic_instance_factory(cls: type[td.GT], *args, **kwds):
    return cls(*args, **kwds)


def generic_make(
    gt_cls: type[td.GT], *, 
    gt_factory: OptInstanceFT = None,
    gt_args: Optional[tuple] = None,
    gt_kwds: Optional[dict] = None) -> td.GT:
    """
    Construct an instance using the given
    factory.
    """

    # Ensure args and kwds are not None.
    args = gt_args or ()
    kwds = gt_kwds or {}

    # Ensure a factory is used to generate an
    # instance.
    factory = gt_factory or basic_instance_factory

    return factory(gt_cls, *args, **kwds)


def compose(*functions: Callable[[td.GT | Any], Any]):
    """
    Defines a new callable which accepts a
    series of functions as its procedure.
    """

    return functools.reduce((lambda func, arg: func(arg)), functions)


CacheFT = Callable[[type[pt.CacheManager]], pt.CacheManager]
"""
Factory which constructs a `CacheManager` object.
"""

OptCacheFT = Optional[CacheFT]
"""Optional `CacheFactory`."""

SessionFT = Callable[[type[requests.Session]], requests.Session]
"""
Factory which constructs a `requests.Session`
object.
"""

OptSessionFT = Optional[SessionFT]
"""Optional `SessionFactory`."""

MetaDataFT = Callable[[], td.MetaData]
"""
Factory which constructs a `MetaData`
mapping.
"""

OptMetaDataFT = Optional[MetaDataFT]
"""Optional `MetaDataFT`."""

TokenMetaDataFT = Callable[[], td.TokenMetaData]
"""
Factory which constructs a `TokenMetaData`
mapping.
"""

OptTokenMetaDataFT = Optional[TokenMetaDataFT]
"""Optional `TokenMetaDataFT`."""
