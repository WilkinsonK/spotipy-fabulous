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
    Configuration values. Specific to OAuth
    requests.
    """

    # Strictly required.
    client_id:     str
    client_secret: str
    code_verifier: str

    # Required, but not mandatory.
    client_userid:    td.OptString
    url_for_redirect: td.OptString

    # Optional.
    code_challenge: td.OptString    = None
    scope:          td.OptAuthScope = None
    state:          td.OptString    = None


@dataclasses.dataclass(slots=True)
class RequestsConfig(SimpleConfig):
    """
    Configuration values. Specific to basic
    requests.
    """

    # Required attributes.
    headers:  td.RequestHeaders

    # Optional.
    timeouts: td.Optional[tuple[float, ...]]
