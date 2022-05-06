"""
spotify/oauth

In this module there are defined a series of objects
that subclass from the `BaseAuthFlow` abstraction. See
base.py for reference.

These objects-- "Auth Flows"-- are designed to obtain
access to Spotify's API by retrieving a token. The
`Spotify API` utilizes OAuth2.0 and it's practices,
the Auth Flows in this module represent those different
practices.

Current available Auth Flows:
* ClientCredentialsFlow
* AuthorizationFlow
* PKCEFlow

NOTE: Because "Implicit Grant" is not a recommened
authentication flow, per `Spotify API` documentation,
there is no object defined for it's purpose.
"""

from spotipy.oauth.auth import ClientCredentialsFlow, \
    AuthorizationFlow, PKCEFlow
