"""
models/base.py

Models based off from `pydantic`. Here you will find
the generics, bases and the types to be associated
with `Spotify Objects`. Deriving all from the same
base class, `SpotifyBaseModel`, all other subsequent
bases and generics are designed for the following
purposes.

See: https://developer.spotify.com/documentation/web-api/reference/#/

```python
fromp spotipy import models

class SomeModel(models.SpotifyBaseModel):

    @classmethod
    def digest(cls, status, payload):
        '''Some code to make object from payload.'''

# returns an instance of `SomeModel`
obj = models.digest({}, model=SomeModel)

print(obj) # Model instance.
print(models.expand(obj)) # Model restored to payload.
```

**Functions**:

- `digest`: Collapses an inbound payload into the
target model.

- `expand`: Restore a model to represent a payload.


**Models**:

- `SpotifyBaseModel`: The base abstraction all models
are derived from.

    :alias: SpotifyModel

    :usage: SpotifyBaseModel

- `SpotifyBaseItem`: Represents a single object.

    :alias: SpotifyItem

    :param: <KT>

    :usage: SpotifyBaseItem[<KT>]

- `SpotifyBaseTyped`: Represents an object which has
an identity.

    :alias: SpotifyTyped

    :param: <SpotifyModel>

    :usage: SpotifyBaseTyped[<SpotifyModel>]

- `SpotifyBaseIterable`: Represents a series of
items in sequence.

    :alias: SpotifyIterable

    :param: <SpotifyModel>

    :usage: SpotifyBaseIterable[<SpotifyModel>]

- `SpotifyBaseCollection`: Represents a series of
typed items in sequence.

    :alias: SpotifyCollection

    :param: <SpotifyModel>

    :usage: SpotifyBaseCollectio[<SpotifyModel>]
"""

import abc, http, itertools, re, typing

from pydantic import BaseModel, validator

import spotipy.errors as errors


KT = typing.TypeVar("KT")
"""Key Type."""

VT = typing.TypeVar("VT")
"""Value Type."""

NT = typing.TypeVar("NT")
"""Node Type."""

UnsignedIntType = typing.TypeVar(
    "UnsignedIntType", bound="UnsignedInt", contravariant=True)
"""
A positive valued, non-floating, number.
"""

class UnsignedInt(int):
    """
    A positive valued, non-floating, number.
    """

    def __new__(cls, value: int | str | bytes | None = None):
        value = int(value or 0)

        if value < 0:
            raise ValueError(
                f"UnsignedInt can only accept "
                f"positive integers, not {value!s}!")
        return super(UnsignedInt, cls).__new__(cls, value)


class SupportsString(typing.Protocol):
    """
    Some object which can be
    represented by and/or
    transformed into a string.
    """

    def __str__(self) -> str:
        ...


UrlRegex = re.compile(
    r"(?:[a-zA-Z]://)?"
    r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
UrlPathType = typing.TypeVar(
    "UrlPathType", bound="UrlPath", contravariant=True)
"""
A string which represents a `URL`.
This includes, protocol, host and
endpoint (optional).
"""

class UrlPath(str):

    def __new__(cls, value: SupportsString):
        if not UrlRegex.fullmatch(str(value)):
            raise ValueError(
                f"expected a valid url. "
                f"{value!r} is not url safe!")
        return super(UrlPath, cls).__new__(cls, value)


SpotifyModel = typing.TypeVar("SpotifyModel", bound="SpotifyBaseModel")
"""
Represents a inbound payload in
the form of an object.
"""

SpotifyPayloadType = typing.TypeVar(
    "SpotifyPayloadType", bound="SpotifyPayload", contravariant=True)
"""
Represents an inbound dataset
from the `Spotify API`.
"""

SpotifyItem = typing.TypeVar("SpotifyItem", bound="SpotifyBaseItem")
"""
Represents a specific object,
from the `Spotify API` which
has been converted to a `Python`
object.
"""

SpotifyTyped = typing.TypeVar("SpotifyTyped", bound="SpotifyBaseTyped")
"""
Represents a specific kind of object
coming from the `Spotify API`.

This object can be considered a
"thing" which has an identity, and
a collection of refrerences to it's
relationships.
"""

SpotifyMap = typing.TypeVar("SpotifyMap", bound="SpotifyBaseMap")
"""
Represents a series of items in
sequence.
"""

SpotifyCollection = typing.TypeVar(
    "SpotifyCollection", bound="SpotifyBaseCollection")
"""
Represents a series of items in
sequence.
"""

SpotifyPayload       = dict[KT, VT] | list | tuple
SpotifyPayloadDigest = dict[str, typing.Any] # Because  Liskov Principle...


class SpotifyBaseModel(abc.ABC, BaseModel, typing.Generic[NT]):
    """
    Represents a inbound payload in
    the form of an object.
    """

    http_status: http.HTTPStatus | UnsignedInt
    """
    Response code from `payload` retrieval.
    """

    @classmethod
    def digest(cls,
        status: UnsignedIntType, payload: SpotifyPayloadType) -> SpotifyModel:
        """
        Breaks the given payload into
        an instance of this `SpotifyModel`.
        """
        return basic_make_model(cls, status, payload)

    @classmethod
    def get_node_cls(cls) -> type[NT]:
        """
        Retrieve the model class attributed
        to this Iterable.
        """

        # Locate the generic alias
        idx = 0
        while (parent := cls.__orig_bases__[idx]): #type: ignore[attr-defined]
            if hasattr(parent, "__args__"):
                break
            idx += 1

        return parent.__args__[0]

    @validator("http_status")
    def validate_status_code(cls, value):
        if isinstance(value, (int, UnsignedInt)):
            value = http.HTTPStatus(value)
        return value

class SpotifyBaseMap(SpotifyBaseModel[SpotifyModel]):
    """
    Represents a series of items in
    sequence.
    """

    items: list[SpotifyModel]
    total: UnsignedInt

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx: int) -> SpotifyModel:
        return self.items[idx]

    @classmethod
    def digest(cls, status: UnsignedIntType, payload: typing.Iterable):
        return iters_make_model(cls, status, payload)


class SpotifyBaseItem(SpotifyBaseModel[VT]):
    """
    Represents a specific object,
    from the `Spotify API` which
    has been converted to a `Python`
    object.
    """

    value: VT

    def __str__(self):
        return f"{type(self).__qualname__}[{self.value!r}]"


class SpotifyBaseTyped(SpotifyBaseModel[SpotifyModel]):
    """
    Represents a specific kind of object
    coming from the `Spotify API`.

    This object can be considered a
    "thing" which has an identity, and
    a collection of refrerences to it's
    relationships.
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

    external_urls: typing.Iterable[UrlPath]
    """
    Known external `URLS` for this object.
    """

    uri: str
    """
    The `Spotify URI` for this object.
    """

    images: typing.Iterable[SpotifyModel]
    """
    Images related to this object.
    """

    @validator("href", "external_urls")
    def validate_urls(cls, value):
        if value:
            return UrlPathType(value)


class SpotifyBaseCollection(SpotifyBaseModel[SpotifyModel]):
    """
    Represents a series of objects
    in sequence.
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

    @validator("limit", "offset")
    def validate_limits(cls, value):
        return UnsignedInt(value)

    @validator("href", "next", "previous")
    def validate_urls(cls, value):
        if value:
            return UrlPath(value)


class SpotifyErrorModel(SpotifyBaseModel):
    """
    Represents the structure of an
    error response from the
    `Spotify API`.
    """

    error: SpotifyPayload
    """
    Inbound error payload.
    """

    @classmethod
    def digest(cls, status: UnsignedIntType, payload: SpotifyPayloadType):
        return cls(http_status=status, error=payload)


def hash_from_schema(cls: type[SpotifyModel],
    status: UnsignedIntType, data: typing.Iterable):
    """
    Breaks down some iterable into
    a hash based on the given
    `SpotifyModel` schema.
    """

    properties = cls.schema()["properties"]

    if isinstance(data, str):
        data = status, data
    else:
        data = (status, *data)

    return dict(itertools.zip_longest(properties, data))


def basic_make_model(cls: type[SpotifyModel],
    status: UnsignedInt, payload: SpotifyPayloadType):
    """
    Standard expected model digestion.
    """

    if not isinstance(payload, dict):
        payload = hash_from_schema(cls, status, payload)
    return cls(http_status=status, **payload)


def iters_make_model(cls: type[SpotifyBaseMap[SpotifyModel]],
    status: UnsignedInt, payload: typing.Iterable):
    """
    Standard iterable model digestion.
    """

    model_cls = cls.get_node_cls()
    items     = [] #type: ignore[var-annotated]
                   # unneeded type annotation.

    for item in payload:
        item = hash_from_schema(model_cls, status, item)
        item.pop("http_status")
        items.append(model_cls.digest(status, item))

    return cls(http_status=status, items=items, total=len(items))


def error_make_model(payload: SpotifyPayloadType):
    """
    Breaks down a given payload
    into a `SpotifyErrorModel` object.
    """

    _payload = hash_from_schema(SpotifyErrorModel, UnsignedInt(0), payload)
    _status  = _payload["error"]["status"]
    return SpotifyErrorModel.digest(_status, _payload)


def digest(payload: SpotifyPayloadDigest, *,
    status: UnsignedInt = None,
    model: type[SpotifyModel] = None) -> SpotifyModel:
    """
    Collapses an inbound payload into
    the target model.

    If the given payload contains the
    key, `error`, instead returns a
    `SpotifyErrorModel`.

    :payload: dict -- inbound JSON object.

    :model: SpotifyModel -- Model to digest
    data into.

    :status: UnsignedInt -- response code.
    """

    if "error" in payload:
        return error_make_model(payload)

    # Assume response status is
    # `CREATED` if none given.
    _status = status or UnsignedInt(201)


    # model param is still a
    # required value.
    # Needs explicit declaration.
    if model is None:
        raise errors.SpotifyValidationError("param 'model' must not be None.")

    return model.digest(_status, payload) #type: ignore[return-value]


EXPANSION_FIELDS_TO_EXCLUDE = {"http_status"}
"""
Fields that are to be ignored on model expansion.
"""


def expand(model: SpotifyModel) -> SpotifyPayloadDigest:
    """
    Restore a model to represent a
    payload.
    """

    payload = model.dict(
        exclude=EXPANSION_FIELDS_TO_EXCLUDE,
        exclude_none=True)

    # If passing in an error,
    # return `error` attribute.
    if isinstance(model, SpotifyErrorModel):
        return payload["error"]
    return payload
