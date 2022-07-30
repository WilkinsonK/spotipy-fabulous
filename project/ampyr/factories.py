"""
Subcategory for typedefs to outline factories
used in this package.
"""

import functools
from typing import Any, Callable, Optional

import requests

from ampyr import  protocols as pt, typedefs as td

GenericFT = Callable[[td.GT], td.GT]
"""Generic factory."""

OptGenericFT = Optional[GenericFT[td.GT]]
"""Optional `GenericFT`."""

InstanceFT = Callable[[type[td.GT]], td.GT]
"""
A generic factory which constructs an instance of
the given type.
"""

OptInstanceFT = Optional[InstanceFT]
"""Optional `InstanceFT`."""


def basic_constructor_ft(cls: type[td.GT], *args, **kwds):
    return cls(*args, **kwds)


def basic_executor_ft(func: Callable, *args, **kwds):
    return func(*args, **kwds)


def basic_passthrough_ft(obj: td.GT, *args, **kwds):
    return obj


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
    factory = gt_factory or basic_constructor_ft

    return factory(gt_cls, *args, **kwds)


def compose(*functions: Callable[[td.GT | Any], Any]):
    """
    Defines a new callable which accepts a
    series of functions as its procedure
    modifing a single object.
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

RESTDriverFT = Callable[[type[pt.RESTDriver]], pt.RESTDriver]
"""
Factory which constructs a `RESTDriver` object.
"""

OptRESTDriverFT = Optional[RESTDriverFT]
"""Optional `RESTDriverFT`."""

OAuth2FlowFT = Callable[[type[pt.OAuth2Flow]], pt.OAuth2Flow]
"""
Factory which constructs a `RESTDriver` object.
"""

OptOAuth2FlowFT = Optional[OAuth2FlowFT]
"""Optional `OAuth2FlowFT`."""
