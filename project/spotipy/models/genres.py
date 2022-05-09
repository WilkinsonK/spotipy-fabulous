from spotipy.models import base


class Genre(base.SpotifyBaseItem[str]):
    """
    String representing some
    genre.
    """


class AvailableGenres(base.SpotifyBaseIterable[Genre]):
    """
    List of available genres seed
    parameter values for
    recommendations.

    :endpoint: /recommendations/available-genre-seeds
    """
