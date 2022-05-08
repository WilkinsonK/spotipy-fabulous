"""
models/base.py
"""
import http
import typing

from pydantic import BaseModel

import spotipy.errors as errors


SpotifyPayload = typing.TypeVar("SpotifyPayload", bound="SpotifyPayloadType")
"""
Represents an inbound dataset
from the `Spotify API`.
"""


SpotifyModel = typing.TypeVar("SpotifyModel", bound="SpotifyBaseModel")
"""
Represents a inbound payload in
the form of an object.
"""

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
class SpotifyPayloadType(dict[KT, VT]):
    ...


class SpotifyBaseModel(BaseModel):
    """
    Represents a inbound payload in
    the form of an object.
    """

    http_status: http.HTTPStatus



class SpotifyErrorModel(SpotifyBaseModel):
    """
    Represents the structure of an
    error response from the
    `Spotify API`.
    """

    error: dict[str, typing.Any]


def digest(payload: SpotifyPayload, *,
    model: type[SpotifyModel] = None) -> SpotifyModel:
    """
    Collapses an inbound payload into
    the target model.

    If the given payload contains the
    key, `error`, instead returns a
    `SpotifyErrorModel`.
    """

    if "error" in payload:
        status = http.HTTPStatus(payload["error"]["status"])
        return SpotifyErrorModel(http_status=status, error=payload) #type: ignore[return-value]

    # Assume response status is
    # `OK`.
    status = http.HTTPStatus(200)

    # model param is still a
    # required value.
    # Needs explicit declaration.
    if model is None:
        raise errors.SpotifyValidationError("param 'model' cannot be None.")

    return model(http_status=status, **payload)


def expand(model: SpotifyModel) -> SpotifyPayload:
    """
    Restore a model to represent a
    payload.
    """

    # If passing in an error,
    # return `error` attribute.
    if isinstance(model, SpotifyErrorModel):
        return model.dict()["error"]

    payload = model.dict()
    payload.pop("http_status")
    return payload #type: ignore[return-value]


class TestModel(SpotifyBaseModel):
    ...

x = digest({"attr1": 200}, model=TestModel)
x = expand(x)
