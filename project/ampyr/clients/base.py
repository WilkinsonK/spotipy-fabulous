"""
Defines basic behavior of objects responsible for
brokering calls to/from a target `Web API`.
"""

from ampyr import factories as ft, protocols as pt, typedefs as td
from ampyr import oauth2


class SimpleRESTDriver(pt.RESTDriver):
    """
    Defines basic behavior such as construction
    of this and derivitive types.
    """


class NullRESTDriver(SimpleRESTDriver):
    """
    This Driver effectively does nothing, hence
    the title `NullRESTDriver`. For each of it's
    methods, theif functionalities are defined
    to make no modifications to their inputs
    and/or return nothing.
    """

    def make_payload(self, data: td.OptRequestHeaders = None):
        if not data:
            return td.RequestHeaders()
        return data

    def make_url(self, *, requires_idn: td.Optional[bool] = None):
        return ""


class SimpleRESTClient(pt.RESTClient):
    """
    Defines basic behavior such as construction
    of this and derivitive types.
    """

    driver: pt.RESTDriver
    """
    Internal functionality for handling REST
    construction.
    """

    oauth2flow: pt.OAuth2Flow
    """
    Internal functionality for brokering calls
    to the authentication host.
    """

    __driver_class__:   type[pt.RESTDriver]
    __driver_factory__: ft.OptRESTDriverFT

    def __init_subclass__(cls, driver=None, **kwds) -> None:
        """
        Construct this type of `RESTClient`.
        """

        super().__init_subclass__(**kwds)

        cls.__driver_class__ = driver or NullRESTDriver

    # Need:
    # 1. Base url
    # 2. Base auth/token urls (optional)
    # 3. OAuth credentials
    #   a. client_id
    #   b. client_secret
    #   c. client_username/id
    # 4. Driver construction factory (optional)
    def __init__(self, *,
        oauth2flow: td.Optional[type[pt.OAuth2Flow]] = None,
        client_id: td.Optional[str] = None,
        client_secret: td.Optional[str] = None,
        driver_factory: ft.OptRESTDriverFT = None):
        """Construct a `RESTClient`."""

        self.__driver_factory__ = driver_factory
