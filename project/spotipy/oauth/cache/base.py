import abc, typing

from spotipy import oauth


class SpotifyCacheHandler(typing.Protocol):

    def save_token_data(self, token_data: oauth.TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    def find_token_data(self) -> oauth.OptionalTokenData:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """


class BaseCacheHandler(abc.ABC):

    @abc.abstractmethod
    def save_token_data(self, token_data: oauth.TokenData) -> None:
        """
        Save the given token data to the cache.
        """

    @abc.abstractmethod
    def find_token_data(self) -> oauth.OptionalTokenData:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """
