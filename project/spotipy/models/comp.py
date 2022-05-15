"""
models/comp.py

Internal component objects.
"""

import enum, typing

from spotipy.models import base


class DatePrecisionEnum(str, enum.Enum):
    """
    Precision with which a date is known.
    """

    YEAR  = "year"
    MONTH = "month"
    DAY   = "day"


class DatePrecision(base.SpotifyBaseItem[DatePrecisionEnum]):
    """
    Represents a `date_precision`
    object.
    """

    @base.validator("value")
    def validate_precion(cls, value):
        return DatePrecisionEnum(value)


class RestrictionEnum(str, enum.Enum):
    """
    The reason for the restriction. Albums may
    be restricted if the content is not available
    in a given market, to the user's subscription
    type, or when the user's account is set to
    not play explicit content. Additional reasons
    may be added in the future.
    """

    MARKET   = "market"   # Out of market range.
    PRODUCT  = "product"  # Limited due to subscription.
    EXPLICIT = "explicit" # Content may be blocked.


class Genre(base.SpotifyBaseItem[str]):
    """
    String representing some
    genre.
    """


class AvailableGenres(base.SpotifyBaseArray[Genre]):
    """
    List of available genres seed
    parameter values for
    recommendations.

    :endpoint: /recommendations/available-genre-seeds
    """


PopularityType = typing.TypeVar(
    "PopularityType", bound="Popularity", contravariant=True)
"""
Some integer value ranging between 0-100.
"""


class Popularity(int):
    """
    Some integer value ranging between 0-100.
    """

    def __new__(cls, value: int | str | bytes | None = None):
        value = (value or 0)

        if not value in range(101):
            raise ValueError(
                f"Popularity can only accept "
                f"values ranging from 0-100, not {value!s}!")
        return super(Popularity, cls).__new__(cls, value)


class Restriction(base.SpotifyBaseItem[RestrictionEnum]):
    """
    Represents a restriction placed
    on some `Spotify Object`.
    """

    @base.validator("value")
    def validate_restriction(cls, value):
        return RestrictionEnum(value)


class MarketCode(base.SpotifyBaseItem[str]):
    """
    A two char string representing
    a country code.

    :standard: `ISO 3166-1 alpha-2`
    See: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    """

    @base.validator("value")
    def validate_code(cls, value):
        if len(value) != 2:
            raise ValueError(f"expected 2 chars for value, got {value}!")
        return value


class AvailableMarkets(base.SpotifyBaseArray[MarketCode]):
    """
    List of available markets where
    `Spotify` is available.

    :endpoint: /markets
    """
