"""
Defines basic behavior of objects responsible for
brokering calls to/from a target `Web API`.
"""

from ampyr import factories as ft, protocols as pt, typedefs as td
from ampyr import oauth2
from ampyr.clients import configs, drivers


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

    @property
    def auth_config(self):
        return self.__auth_config__

    @property
    def url_config(self):
        return self.__url_config__

    __auth_config__: configs.AuthConfig
    __url_config__:  configs.UrlConfig

    __driver_class__: type[pt.RESTDriver]
    __oauth_class__:  type[pt.OAuth2Flow]

    __driver_factory__: ft.OptRESTDriverFT
    __oauth_factory__:  ft.OptOAuth2FlowFT

    def __init_subclass__(cls, driver=None, **kwds) -> None:
        """
        Construct this type of `RESTClient`.
        """

        super().__init_subclass__(**kwds)

        cls.__driver_class__ = driver or drivers.NullRESTDriver

    # Need:
    # 1. Base url
    # 2. Base auth/token urls (optional)
    # 3. OAuth credentials
    #   a. client_id
    #   b. client_secret
    #   c. client_username/id
    # 4. Driver construction factory (optional)
    def __init__(self, url_for_host: str, *,
        url_for_oauth: td.OptString = None,
        url_for_redirect: td.OptString = None,
        endpoint_for_oauth: td.OptString = None,
        endpoint_for_token: td.OptString = None,
        oauth2flow: td.Optional[type[pt.OAuth2Flow]] = None,
        client_id: td.OptString = None,
        client_secret: td.OptString = None,
        client_userid: td.OptString = None,
        driver_factory: ft.OptRESTDriverFT = None,
        oauth_factory: ft.OptOAuth2FlowFT = None):
        """Construct a `RESTClient`."""

        self.__driver_factory__ = driver_factory
        self.__oauth_factory__  = oauth_factory

        self.__oauth_class__ = oauth2flow or oauth2.NullFlow

        self._new_auth_config(
            client_id=client_id,
            client_secret=client_secret,
            client_userid=client_userid)

        self._new_url_config(
            url_for_host=url_for_host,
            url_for_oauth=url_for_oauth,
            url_for_redirect=url_for_redirect,
            endpoint_for_oauth=endpoint_for_oauth,
            endpoint_for_token=endpoint_for_token)

        self._new_oauthflow()

    def _new_auth_config(self, *args, **kwds):
        """
        Generates a configuration object for
        auth values.
        """

        inst = ft.generic_make(
            configs.AuthConfig,
            gt_kwds=kwds,
            gt_args=args)

        self.__auth_config__ = inst

    def _new_url_config(self, url_for_host: str, *args, **kwds):
        """
        Generates a configuration object for
        URL values.
        """

        if not kwds["url_for_oauth"]:
            kwds["url_for_oauth"] = url_for_host

        if not kwds["endpoint_for_oauth"]:
            kwds["endpoint_for_oauth"] = "authorize"

        # What's the smarter way to handle this?
        if not kwds["endpoint_for_token"]:
            kwds["endpoint_for_token"] = "api/token"

        kwds["url_for_host"] = url_for_host

        inst = ft.generic_make(
            configs.UrlConfig,
            gt_kwds=kwds,
            gt_args=args)

        self.__url_config__ = inst

    def _new_oauthflow(self, **kwds):
        """
        Generates a new `OAuth2Flow` object
        according to the spec provided in this
        `RESTClient`.
        """

        gt_args = (
            self.auth_config.client_id,
            self.auth_config.client_secret)

        gt_kwds = {}

        # Parse oauth string
        gt_kwds["url_for_oauth"] = "/".join([
            self.url_config.url_for_oauth,
            self.url_config.endpoint_for_oauth])

        # Parse token string
        gt_kwds["url_for_token"] = "/".join([
            self.url_config.url_for_oauth,
            self.url_config.endpoint_for_token])

        gt_kwds["client_userid"]    = self.auth_config.client_userid
        gt_kwds["url_for_redirect"] = self.url_config.url_for_redirect

        # Allow for overrides of the above
        # parsing.
        gt_kwds.update(kwds)

        inst = ft.generic_make(
            self.__oauth_class__,
            gt_factory=self.__oauth_factory__,
            gt_kwds=gt_kwds,
            gt_args=gt_args)

        self.oauth2flow = inst
