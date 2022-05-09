import enum

from spotipy.models import base


class Restriction(str, enum.Enum):
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


class RestrictionItem(base.SpotifyBaseItem[Restriction]):
    """
    Represents a restriction placed
    on some `Spotify Object`.
    """

    @base.validator("value")
    def validate_restriction(cls, value):
        return Restriction(value)
