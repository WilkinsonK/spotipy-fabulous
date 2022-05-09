from spotipy.models import base


class Genre(base.SpotifyBaseModel):
    """
    String representing some
    genre.
    """

    value: str

    def __str__(self):
        return self.value

    @classmethod
    def digest(cls,
        status: base.UnsignedIntType, payload: base.SpotifyPayloadType):

        return base.basic_make_model(cls, status, payload)


class AvailableGenres(base.SpotifyBaseIterable[Genre]):
    """
    List of available genres seed
    parameter values for
    recommendations.

    :endpoint: /recommendations/available-genre-seeds
    """
