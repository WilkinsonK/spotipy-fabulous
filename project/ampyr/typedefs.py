"""
Generic types used at the top level of this
package.
"""

from os import PathLike
from pathlib import Path
from typing import NewType, TypedDict, TypeVar # Keep these separate.
from typing import Any, Literal, Optional, Sequence, Generator

from requests import Session

# --------------------------------------------- #
# Generic Types.
# --------------------------------------------- #

GT = TypeVar("GT")
"""Some generic unbound `TypeVar`."""

GT_co = TypeVar("GT_co", covariant=True)
"""Some generic unbound covariant `TypeVar`."""

GT_ct = TypeVar("GT_ct", contravariant=True)
"""
Some generic unbound contravariant `TypeVar`.
"""

OptionalGT = Optional[GT]
"""Optional generic unbound `TypeVar`."""

# --------------------------------------------- #
# Numbers and Enums.
# --------------------------------------------- #

IntSuccess = Literal[0]
IntFailure = Literal[1]
ReturnState = Literal[IntSuccess, IntFailure]
"""
Integer values representing states of
success or failure.
"""

# --------------------------------------------- #
# Strings and Bytes.
# --------------------------------------------- #

StrOrBytes = str | bytes
"""Either string or byte array."""

CharToken = NewType("CharToken", str)
"""
An array of characters in sequence used typically
for auth, identification or encryption.
"""

OptString = Optional[str]
"""Optional string."""

AuthScope = str | Sequence[str]
"""
A string, or series of strings, used to describe
the allowed boundaries for an application to
access.
"""

OptAuthScope = Optional[AuthScope]
"""Optional `AuthScope`."""

FilePath = Path | PathLike[str] | PathLike[bytes] | str | bytes
"""Some path for a file location or directory."""

OptFilePath = Optional[FilePath]
"""Optional `FilePath` object."""

# --------------------------------------------- #
# Structures and Mappings.
# --------------------------------------------- #

MetaData = NewType("MetaData", dict[str, Any])
"""
Generic meta-mapping. Used for instance
contruction.
"""

OptMetaData = Optional[MetaData]
"""Optional generic `MetaData`."""


class TokenMetaData(TypedDict, total=False):
    """Data related to Authentication Tokens."""

    access_token:  CharToken
    refresh_token: CharToken

    grant_type: str
    scope:      AuthScope

    expires_in: int
    expires_at: int


OptTokenMetaData = Optional[TokenMetaData]
"""Optional `TokenMetaData`."""


class RequestHeaders(TypedDict):
    """
    Meta data specifically used in a `RESTful`
    callout.
    """


class ResponseHeaders (TypedDict):
    """
    Meta data specifically used in the response
    from a `RESTful` callout.
    """


OptRequestHeaders = Optional[RequestHeaders]
"""Optional `RequestHeaders` map."""

OptResponseHeaders = Optional[ResponseHeaders]
"""Optional `RequestHeaders` map."""
