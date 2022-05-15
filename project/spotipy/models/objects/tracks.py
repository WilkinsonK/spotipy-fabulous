from spotipy.models import base


class Track(base.SpotifyBaseItem):
    ...


class Tracks(base.SpotifyBaseArray[Track]):
    """
    Array of `Tracks` from the `Spotify API`.
    """


class TracksGroup(base.SpotifyBaseGroup[Tracks]):
    """
    A collection of `Tracks` as a query
    result.
    """
