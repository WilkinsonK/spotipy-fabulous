import typing

from pydantic import validator

from spotipy.models import base


class MarketCode(base.SpotifyBaseModel):
    """
    A two char string representing
    a country code.
    """

    value: str

    def __str__(self):
        return self.value

    @classmethod
    def digest(cls,
        status: base.UnsignedIntType, payload: base.SpotifyPayloadType):

        return base.basic_make_model(cls, status, payload)

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
