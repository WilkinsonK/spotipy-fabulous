import typing

from pydantic import validator

from spotipy.models import base


class MarketCode(base.SpotifyBaseItem[str]):
    """
    A two char string representing
    a country code.
    """

    @validator("value")
    def validate_code(cls, value):
        if len(value) != 2:
            raise ValueError(f"expected 2 chars for value, got {value}!")
        return value


class AvailableMarkets(base.SpotifyBaseIterable[MarketCode]):
    """
    List of available markets where
    `Spotify` is available.

    :endpoint: /markets
    """


if __name__ == "__main__":
    x = base.digest(["CA", "MX", "US"], model=AvailableMarkets)

    for i in x:
        print(i)
