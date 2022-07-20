"""
Definitions below are for the interfaces used in
this package.
"""

from abc import abstractmethod
from typing import Protocol

from ampyr import typedefs as td


class RemoteAccessManager(Protocol):
    """
    Connects to some remote host or service.
    """

    @abstractmethod
    def detach(self) -> td.ReturnState:
        """Disconnects from the target."""

    @abstractmethod
    def attach(self) -> td.ReturnState:
        """Connects to the target."""

    @abstractmethod
    def ping(self) -> td.ReturnState:
        """
        Sends a ping returning the state of the
        target.
        """


class CacheManager(Protocol[td.GT]):
    """
    Brokers transactions of cached data.
    Primarily for the use of relieving more
    expensive transactions.
    """

    @abstractmethod
    def find(self, key: str) -> None | td.GT:
        """
        Attempt to retrieve data from the cache
        assigned to the given key. Returns `None`
        if it fails.
        """

    @abstractmethod
    def save(self, key: str, data: td.GT) -> td.GT:
        """
        Attempt to insert data into the cache,
        assigning it to the given key.
        """


class HasCacheHandler(Protocol):
    """
    Some object which has an attribute named
    'cache_manager' and is of type
    `CacheManager`.
    """

    cache_manager: CacheManager
    """Brokers data to/from some cache."""


class OAuth2Flow(Protocol):
    """
    Represents an Authentication Flow procedure
    defined by `OAuth2.0`. This object is
    responsible for aquiring an authentication
    token.
    """

    @abstractmethod
    def aquire(self) -> td.CharToken:
        """Attempt to retrieve an auth token."""


class MetaConfig(Protocol):
    """
    Some family or group of attributes intended
    for a specific purpose.
    """

    def asdict(self) -> td.MetaData:
        """
        Breaks down this `MetaConfig` into
        a dictionary.
        """
