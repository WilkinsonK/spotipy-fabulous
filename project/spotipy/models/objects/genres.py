from spotipy.models import base


class GenreItem(base.SpotifyBaseItem[str]):
    """
    String representing some
    genre.
    """


class AvailableGenresIterable(base.SpotifyBaseArray[GenreItem]):
    """
    List of available genres seed
    parameter values for
    recommendations.

    :endpoint: /recommendations/available-genre-seeds
    """
