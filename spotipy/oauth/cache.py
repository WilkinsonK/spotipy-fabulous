import abc
import typing


class SpotifyCacheHandler(typing.Protocol):

    def cache_token_data(self, token_data: dict[str, typing.Any]) -> None:
        """
        Save the given token data to the cache
        """

    def find_token_data(self) -> dict[str, typing.Any] | None:
        """
        Retrieve token data from the cache. If
        not found, return `None`
        """

    def __enter__(self) -> "SpotifyCacheHandler":
        ...

    def __exit__(self, etype, evalue, tback) -> None:
        ...


class BaseCacheHandler:

    pass
