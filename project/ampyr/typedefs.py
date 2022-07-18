"""
Generic types used at the top level of this
package.
"""

from typing import Any, Literal, NewType, TypedDict, TypeVar


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

CharToken = TypeVar("CharToken", str, bytes)
"""
An array of characters in sequence used typically
for auth, identification or encryption.
"""

# --------------------------------------------- #
# Structures and Mappings.
# --------------------------------------------- #

MetaData = NewType("MetaData", dict[str, Any])
"""
Generic meta-mapping. Used for instance
contruction.
"""


class TokenMetaData(TypedDict):
    """Data related to Authentication Tokens."""

    access_token: str
    expires_in: int
    expires_at: int
