"""
Describes a series of objects based of the
`RESTDriver` protocol.
"""

from ampyr import protocols as pt, typedefs as td


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
