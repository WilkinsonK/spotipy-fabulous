import typing

from spotipy.models import base, comp


class Artist(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    artist.

    :endpoint: /artists
    """

    followers: typing.Mapping[str, base.UrlPath | int]
    """
    Information about the followers of
    this artist.
    """

    genres: comp.AvailableGenres
    """Genres this artist is associated with."""

    popularity: comp.Popularity
    """Popularity of this artist."""


class Artists(base.SpotifyBaseArray[Artist]):
    """
    Array of `Artists` from the `Spotify API`.
    """


class ArtistsGroup(base.SpotifyBaseGroup[Artists]):
    """
    A collection of `Artists` as a query
    result.
    """
