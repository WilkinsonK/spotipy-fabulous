"""
auth/scopes.py

Tools for manipulating access scope.
"""

import re
import typing

# Identify values in a string separated
# either by a single space or a comma.
EXPECTED_SCOPE_FORMAT = re.compile(r"\w+[, ]{1}")


@typing.overload
def normalize_scope(value: str):
    ...


@typing.overload
def normalize_scope(value: typing.Iterable[str]):
    ...


def normalize_scope(value: str):
    """
    Transform the passed value to
    something consumable by the `Spotify API`.
    """

    if isinstance(value, str):
        value = EXPECTED_SCOPE_FORMAT.split(value)
    return " ".join(value)


def scope_is_subset(subset: str, scope: str):
    """
    Determines if the `subset`
    string is contained in the scope
    `scope`.
    """

    # If either of the given
    # values are `None`, check
    # to see if they both are.
    if None in (subset, scope):
        return subset == scope

    subset = set(EXPECTED_SCOPE_FORMAT.split(subset))
    scope  = set(EXPECTED_SCOPE_FORMAT.split(scope))

    return subset <= scope
