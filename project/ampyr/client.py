

SPOTIFY_BASE_URL = "https://accounts.spotify.com"

SPOTIFY_API_VERSION = "v1"

SPOTIFY_OAUTH_URL = f"{SPOTIFY_BASE_URL}/authorize"
SPOTIFY_TOKEN_URL = f"{SPOTIFY_BASE_URL}/api/token"


class Resource:

    def get(self, *, limit: int = None):
        ...

    def post(self):
        ...

    def push(self):
        ...

    def delete(self):
        ...


class Spotify:

    users:   Resource
    tracks:  Resource
    albums:  Resource
    artists: Resource    


inst = Spotify()
inst.users.get(limit=1)
