import typing

from spotipy.models import base, comp
from spotipy.models.objects import episodes


class Show(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    show.
    """

    available_markets: comp.AvailableMarkets
    """
    List of countries this show can
    be played.
    """

    copyrights: typing.Mapping[str, str]
    """Copyright statements of this show."""

    description: str
    """Description of this show."""

    html_description: str
    """
    Description of this show.
    May contain `HTML` tags.
    """

    explicit: bool
    """
    Whether or not this show has
    explicit content.
    """

    is_externally_hosted: bool | None
    """
    Whether or not this shows episodes
    are hosted outside of `Spotify`'s
    CDN.

    This field might be null in some
    cases.
    """

    languages: typing.Sequence[str]
    """List of languages used in this show."""

    media_type: str
    """The media type of this show."""

    publisher: str
    """The publisher of this show."""

    episodes: episodes.EpisodesGroup
    """Episodes of this show."""


class Shows(base.SpotifyBaseArray[Show]):
    """
    Array of `Shows` from the `Spotify API`.
    """


class ShowsGroup(base.SpotifyBaseGroup[Shows]):
    """
    A collection of `Shows` as a query
    result.
    """
