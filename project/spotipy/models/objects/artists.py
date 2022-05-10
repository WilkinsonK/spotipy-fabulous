from spotipy.models import base


class ArtistTyped(base.SpotifyBaseTyped):
    ...


class ArtistsIterable(base.SpotifyBaseIterable[ArtistTyped]):
    ...


class ArtistsCollection(base.SpotifyBaseCollectionItem):
    ...
