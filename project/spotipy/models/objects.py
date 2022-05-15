import datetime, typing

from spotipy.models import base, comp


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

    restrictions: comp.Restriction
    """
    Included in the response when a content
    restriction is applied.

    Usually, there is only one mapping here,
    "reason" -> `RestrictionItem`. This
    should represent why the album may be
    restricted.
    """

    artists: "Artists"
    """The artists who contributed to this album."""

    tracks: "TracksGroup"
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


class Episode(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    album.

    :endpoint: /episodes
    """

    audio_preview_url: base.UrlPath
    """
    A URL to a 30 second preview of this
    episode. (MP3 format)
    """

    description: str
    """Description of this episode."""

    html_description: str
    """
    Description of this episode.
    May contain `HTML` tags.
    """

    duration_ms: int
    """
    Length of this episode in
    milliseconds.
    """

    explicit: bool
    """
    Whether or not this episode has
    explicit content.
    """

    is_externally_hosted: bool | None
    """
    Whether or not this episode is
    hosted outside of `Spotify`'s
    CDN.

    This field might me null in some
    cases.
    """

    is_playable: bool
    """
    Whether or not this episode
    is playable in the given
    market.
    """

    language: str
    """
    `ISO 639` code representing the
    language spoken in this episode.
    """

    languages: typing.Sequence[str]
    """
    `ISO 639-1` codes representing
    the languages spoken in this
    episode.
    """

    release_date: datetime.date
    """Date this episode was released."""

    release_date_precision: comp.DatePrecision
    """Accuracy which `release_date` is known."""

    resume_point: comp.ResumePoint
    """
    The user's most recent position
    on this episode.
    """

    restrictions: comp.Restriction
    """
    Included in the response when a content
    restriction is applied.

    Usually, there is only one mapping here,
    "reason" -> `RestrictionItem`. This
    should represent why the episode may be
    restricted.
    """

    show: "Show"
    """The show which this episode belongs to."""


class Episodes(base.SpotifyBaseArray[Episode]):
    """
    Array of `Episodes` from the `Spotify API`.
    """


class EpisodesGroup(base.SpotifyBaseGroup[Episodes]):
    """
    A collection of `Episodes` as a query
    result.
    """


class Show(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    show.

    :endpoint: /shows
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

    episodes: EpisodesGroup
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


class Track(base.SpotifyBaseTyped):
    """
    Catalog information for a single
    track.
    """

    album: Album
    """Album which this track belongs to."""

    artists: Artists
    """Artists who contributed to this track."""

    available_markets: comp.AvailableMarkets
    """
    List of countries this track
    can be played.
    """

    disc_number: int
    """
    The disc number (usually '1',
    unless the parent album contains
    multiple discs).
    """

    duration_ms: int
    """The track length in milliseconds."""

    explicit: bool
    """
    Whether or not this track has explicit
    content.
    """

    external_ids: typing.Mapping[str, str]
    """Known external ids for this track."""

    is_playable: bool
    """
    Whether or not this track
    is playable in the given
    market.
    """

    linked_from: "Track" | None
    """
    Part of the response when track
    relinking is applied, and the
    requested track has been replaced
    with a different track.

    This `linked_from` track contains
    information about the originally
    requested track.
    """

    restrictions: comp.Restriction
    """
    Included in the response when a content
    restriction is applied.

    Usually, there is only one mapping here,
    "reason" -> `RestrictionItem`. This
    should represent why the track may be
    restricted.
    """

    popularity: comp.Popularity
    """Popularity of this track."""

    preview_url: base.UrlPath | None
    """
    A URL to a 30 second preview of this
    episode. (MP3 format)

    Can be null.
    """

    track_number: int
    """
    The number of the track.
    If the parent album has multiple
    discs, the track number is the
    number on the relative disc.
    """

    is_local: bool
    """
    Whether or not the track is from
    the local file.
    """


class Tracks(base.SpotifyBaseArray[Track]):
    """
    Array of `Tracks` from the `Spotify API`.
    """


class TracksGroup(base.SpotifyBaseGroup[Tracks]):
    """
    A collection of `Tracks` as a query
    result.
    """
