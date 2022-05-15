import datetime
import typing

from spotipy.models import base, comp
from spotipy.models.objects import artists, tracks

class Album(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    album.

    :endpoint: /albums
    """

    album_type: str
    """The type of this album."""

    total_tracks: int
    """Total number of tracks on this album."""

    available_markets: comp.AvailableMarkets
    """Markets where this album is available."""

    release_date: datetime.date
    """Date this album was released."""

    release_date_presicion: comp.DatePrecision
    """Accuracy which `release_date` is known."""

    restrictions: typing.Mapping[str, comp.Restriction]
    """
    Included in the response when a content
    restriction is applied.

    Usually, there is only one mapping here,
    "reason" -> `RestrictionItem`. This
    should represent why the album may be
    restricted.
    """

    artists: artists.Artists
    """The artists who contributed to this album."""

    tracks: tracks.TracksGroup
    """The tracks on this album."""


class Albums(base.SpotifyBaseArray[Album]):
    """
    Array of `Albums` from the `Spotify API`.
    """


class AlbumsGroup(base.SpotifyBaseGroup[Albums]):
    """
    A collection of `Albums` as a query
    result.
    """
