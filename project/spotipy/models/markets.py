import typing

from pydantic import validator

from spotipy.models import base


MarketCode = typing.TypeVar("MarketCode", bound="MarketCodeType")
"""
A two char string representing
a country code.
"""

Markets = typing.TypeVar("Markets", bound="MarketsType")
"""
Array of `MarketCode` objects.
"""

MarketCodeType = str
MarketsType = list[MarketCode]


class AvailableMarkets(base.SpotifyBaseModel, typing.Generic[Markets]):
    """
    List of available markets where
    `Spotify` is available.

    :endpoint: /markets
    """

    markets: Markets
    """
    Array of `MarketCode` objects.
    """
