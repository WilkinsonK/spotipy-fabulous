import typing

import requests

from spotipy.oauth import cache, utils
from spotipy.oauth.auth import base


def _get_token_data(
    auth_flow: base.BaseAuthFlow, payload: dict[str, typing.Any]):
    """
    Sends an outbound auth call requesting
    for a token.
    """

    # Build a request using the
    # internal session.
    auth = utils.auth_string(
        auth_flow.credentials.client_id,
        auth_flow.credentials.client_secret)

    resp = auth_flow.session.post(
        auth_flow.token_url,
        data=payload,
        headers={"Authorization": auth})

    # Test if there was an issue
    # from the callout, handle any
    # subsequent errors.
    try:
        resp.raise_for_status()
    except requests.HTTPError as error:
        utils.handle_http_error(error)
    else:
        token_data = resp.json()
        utils.set_expires_at(token_data)

        return token_data


class TokenPayloadFactory(typing.Protocol):
    """
    A useful pre-get_token_data hook.
    Intended for the user to manipulate
    the request payload before the
    callout.
    """

    @staticmethod
    def __call__() -> dict[str, typing.Any]:
        ...


def basic_payload_factory():
    """
    Returns a dummy payload with no data.
    """

    return {}


def get_token_data(
    auth_flow: base.BaseAuthFlow,
    cursor: cache.SpotifyCacheHandler,
    payload_factory: TokenPayloadFactory = None):
    """
    Retrieves an access token from the
    `Spotify API`. This function first checks,
    and validates for token data that
    may have been previously cached.
    """

    ts = utils.TokenState

    # Initial lookup for a token from
    # the `auth_flow`'s cache handler.
    token_data = cursor.find_token_data()

    # Validate the token data found.
    # not unlike for parking...
    scope        = auth_flow.credentials.scope
    token_state  = utils.validate_token(token_data, auth_scope=scope)

    if token_state is ts.VALID:
        return token_data

    if token_state is ts.REFRESH:
        payload = {
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token"
        }
    else:
        if not payload_factory:
            payload_factory = basic_payload_factory
        payload = payload_factory()

    # Token either required a refresh
    # or was invalid. Get new token data
    # and try again.
    token_data = _get_token_data(auth_flow, payload)
    if "scope" not in token_data:
        token_data["scope"] = scope
    cursor.save_token_data(token_data)

    return get_token_data(auth_flow, cursor, payload_factory)


def find_token_data(
    auth_flow: base.BaseAuthFlow,
    factory: TokenPayloadFactory) -> utils.TokenData:
    """
    Find valid auth token data.
    """

    # Args required to open the cache
    # pool.
    hcls, hkwds = auth_flow.cache_cls, auth_flow.cache_params

    with cache.SpotifyCachePool(hcls, hkwds=hkwds) as cpool:
        curs = cpool.new()
        return get_token_data(auth_flow, curs, factory)
