import typing

from spotipy import models
from spotipy.models import base


class MarketCodeItem(base.SpotifyBaseItem[str]):
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


class AvailableMarketsIterable(base.SpotifyBaseArray[MarketCodeItem]):
    """
    List of available markets where
    `Spotify` is available.

    :endpoint: /markets
    """


if __name__ == "__main__":
    x = models.digest(["CA", "MX", "US"], model=AvailableMarketsIterable)

    for i in x:
        print(i)
