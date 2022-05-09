import datetime, enum

from spotipy.models import base, components, markets


class AlbumModel(base.SpotifyBaseTyped):
    """
    An album.

    :endpoint: /albums/{id}
    """

    album_type: str
    """
    The type of the album.
    """

    total_tracks: int
    """
    Number of tracks in the album.
    """

    available_markets: markets.AvailableMarketsIterable
    """
    MarketCodes where this album is
    available.
    """

    release_date: datetime.date
    """
    When this album was first
    released.
    """

    release_date_precision: components.DatePrecisionItem
    """
    Precision with which `release_date`
    value is known.
    """

    restrictions: dict[str, components.Restriction]
    """
    Included in the response when a
    content restriction is applied.
    """
