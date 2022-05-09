"""
models/base.py
"""

import abc
import http
import re
import typing

from pydantic import BaseModel, validator

import spotipy.errors as errors


KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")

UnsignedInt = typing.TypeVar("UnsignedInt", bound="UnsignedIntType")
"""
A positive valued, non-floating, number.
"""

class UnsignedIntType(int):

    def __new__(cls, value: int | str | bytes | None = None):
        value = int(value or 0)

        if value < 0:
            raise ValueError(
                f"UnsignedInt can only accept "
                f"positive integers, not {value!s}!")
        return super(UnsignedIntType, cls).__new__(cls, value)


class SupportsString(typing.Protocol):
    """
    Some object which can be
    represented by and/or
    transformed into a string.
    """

    def __str__(self) -> str:
        ...


UrlRegex = re.compile(r"(?:[a-zA-Z]://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
UrlPath  = typing.TypeVar("UrlPath", bound="UrlPathType")
"""
A string which represents a `URL`.
This includes, protocol, host and
endpoint (optional).
"""

class UrlPathType(str):

    def __new__(cls, value: SupportsString):
        if not UrlRegex.fullmatch(str(value)):
            raise ValueError(
                f"expected a valid url. "
                f"{value!r} is not url safe!")
        return super(UrlPathType, cls).__new__(cls, value)


SpotifyModel = typing.TypeVar("SpotifyModel", bound="SpotifyBaseModel")
"""
Represents a inbound payload in
the form of an object.
"""

SpotifyPayload = typing.TypeVar("SpotifyPayload", bound="SpotifyPayloadType")
"""
Represents an inbound dataset
from the `Spotify API`.
"""

SpotifyPayloadType   = dict[KT, VT]
SpotifyPayloadDigest = dict[str, typing.Any] # Because  Liskov Principle...


class SpotifyBaseModel(abc.ABC, BaseModel, typing.Generic[UnsignedInt]):
    """
    Represents a inbound payload in
    the form of an object.
    """

    http_status: http.HTTPStatus | UnsignedInt
    """
    Response code from `payload` retrieval.
    """

    @abc.abstractmethod
    @classmethod
    def digest(cls,
        status: UnsignedInt, payload: SpotifyPayload) -> "SpotifyBaseModel":
        """
        Breaks the given payload into
        an instance of this `SpotifyModel`.
        """

    @validator("http_status")
    def validate_status_code(cls, value):
        if isinstance(value, UnsignedInt):
            value = http.HTTPStatus(value)
        return value


def basic_make_model(cls: type[SpotifyModel],
    status: UnsignedInt, payload: SpotifyPayloadDigest):
    """
    Standard expected model digestion.
    """

    return cls(http_status=status, **payload)


class SpotifyBaseTyped(
    SpotifyBaseModel, typing.Generic[UrlPath, SpotifyModel]):
    """
    Represents a specific kind of
    object coming from the
    `Spotify API`.
    """

    id: str
    """
    The `Spotify ID` for this object.
    """

    type: str
    """
    The object type.
    """

    name: str
    """
    The name of the object.
    """

    href: UrlPath
    """
    A link to the `Web API` endpoint for this object.
    """

    external_urls: list[UrlPath]
    """
    Known external `URLS` for this object.
    """

    uri: str
    """
    The `Spotify URI` for this object.
    """

    images: list[SpotifyModel]
    """
    Images related to this object.
    """

    @classmethod
    def digest(cls, status: UnsignedInt, payload: SpotifyPayload):
        return basic_make_model(cls, status, payload)

    @validator("href", "external_urls")
    def validate_urls(cls, value):
        if value:
            return UrlPathType(value)


class SpotifyBaseCollection(
    SpotifyBaseModel, typing.Generic[SpotifyModel, UnsignedInt, UrlPath]):
    """
    Represents a series of items in
    sequence.
    """

    items: typing.Iterable[SpotifyModel]
    """
    The requested content.
    """

    # Query limits
    limit: UnsignedInt
    """
    The maximum number of items in the
    response.
    """

    offset: UnsignedInt
    """
    The offset of items returned.
    """

    total: UnsignedInt
    """
    The total number of items available
    to return.
    """

    # Urls
    href: UrlPath
    """
    Link to the `Web API` endpoint
    providing full result of the request.
    """

    next: UrlPath | None
    """
    `URL` to the next page of items.
    """

    previous: UrlPath | None
    """
    `URL` to the previous page of
    items.
    """

    @classmethod
    def digest(cls, status: UnsignedInt, payload: SpotifyPayload):
        items = {}
        for key, coll in payload.items():
            items[key] = basic_make_model(cls, status, coll)
        return cls(http_status=status, **payload)

    @validator("limit", "offset")
    def validate_limits(cls, value):
        return UnsignedIntType(value)

    @validator("href", "next", "previous")
    def validate_urls(cls, value):
        if value:
            return UrlPathType(value)


class SpotifyErrorModel(SpotifyBaseModel, typing.Generic[SpotifyPayload]):
    """
    Represents the structure of an
    error response from the
    `Spotify API`.
    """

    error: SpotifyPayload
    """
    Inbound error payload.
    Parsed from:

    ```json
    {
        "error": {
            "status": 400,
            "message": "string"
        }
    }
    ```
    """

    @classmethod
    def digest(cls, status: UnsignedInt, payload: SpotifyPayloadDigest):
        return cls(http_status=status, error=payload)


def digest(payload: SpotifyPayload, *,
    status: UnsignedInt = None,
    model: type[SpotifyModel] = None) -> SpotifyModel:
    """
    Collapses an inbound payload into
    the target model.

    If the given payload contains the
    key, `error`, instead returns a
    `SpotifyErrorModel`.
    """

    if "error" in payload:
        _status = UnsignedIntType(payload["error"]["status"])
        return SpotifyErrorModel.digest(_status, payload)

    # Assume response status is
    # `CREATED` if none given.
    _status = status or UnsignedIntType(201)

    # model param is still a
    # required value.
    # Needs explicit declaration.
    if model is None:
        raise errors.SpotifyValidationError("param 'model' must not be None.")

    return model(http_status=_status, **payload)


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
