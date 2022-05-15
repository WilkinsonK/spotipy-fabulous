from spotipy.models import base, comp


class Episode(base.SpotifyBaseTyped):
    ...


class Episodes(base.SpotifyBaseArray[Episode]):
    """
    Array of `Episodes` from the `Spotify API`.
    """


class EpisodesGroup(base.SpotifyBaseGroup[Episodes]):
    """
    A collection of `Episodes` as a query
    result.
    """
