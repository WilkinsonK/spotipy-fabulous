"""`MetaConfigs` specific to this sub-package."""

import dataclasses

from ampyr import protocols as pt, typedefs as td


@dataclasses.dataclass
class SimpleConfig(pt.MetaConfig):

    def asdict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass(slots=True)
class AuthConfig(SimpleConfig):
    """
    Config values specific to authentication
    used in the parent `RESTClient` object.
    """

    client_id:     str
    client_secret: str

    # Optionals.
    client_userid: td.OptString = None


@dataclasses.dataclass(slots=True)
class UrlConfig(SimpleConfig):
    """
    Config values specific to URLs used in the
    parent `RESTClient` object.
    """

    # Required values.
    url_for_host:       str
    url_for_oauth:      str
    endpoint_for_oauth: str
    endpoint_for_token: str

    # Optionals.
    url_for_redirect: td.OptString = None
