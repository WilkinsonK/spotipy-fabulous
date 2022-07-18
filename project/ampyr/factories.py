"""
Subcategory for typedefs to outline factories
used in this package.
"""

from typing import Callable

from ampyr import typedefs as td

InstanceFactory = Callable[[type[td.GT]], td.GT]
"""
A generic factory which constructs an instance of
the given type.
"""


def basic_instance_factory(cls: type[td.GT], *args, **kwds):
    return cls(*args, **kwds)


def generic_make(
    gt_cls: type[td.GT], *, 
    gt_factory: None | InstanceFactory = None,
    gt_args: None | tuple = None,
    gt_kwds: None | dict = None) -> td.GT:
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
