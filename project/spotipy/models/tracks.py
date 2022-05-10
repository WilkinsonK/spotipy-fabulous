from spotipy.models import base


class TrackTyped(base.SpotifyBaseTyped):
    ...


class TracksCollection(base.SpotifyBaseCollection[TrackTyped]):
    ...
