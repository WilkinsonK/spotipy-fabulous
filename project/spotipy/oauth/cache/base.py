import abc
import typing

from spotipy.oauth import utils

class SpotifyCacheHandler(typing.Protocol):

    def save_token_data(self, token_data: utils.TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    def find_token_data(self) -> utils.TokenData | None:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """


class BaseCacheHandler(abc.ABC):

    @abc.abstractmethod
    def save_token_data(self, token_data: utils.TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    @abc.abstractmethod
    def find_token_data(self) -> utils.TokenData | None:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """
