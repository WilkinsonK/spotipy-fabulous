"""
auth/sessions.py

Tools for building sessions.
"""

import types
import typing

import requests


class SpotifySession(requests.Session):
    pass


class SessionFactory(typing.Protocol):

    @staticmethod
    def __call__(cls: type[SpotifySession]) -> types.ModuleType | SpotifySession:
        ...


def basic_session_factory(cls: type[SpotifySession]):
    if not cls:
        return requests.api
    return cls()


def make_session(
    session: SpotifySession,
    session_factory: SessionFactory = None):
    """
    Generate a `SpotifySession` object.

    if `session` is `None` or a type of `Session`,
    build new session object using the
    `session_factory`.
    """

    if not session_factory:
        session_factory = basic_session_factory

    # We assume if no active session
    # is passed, that it is either
    # a `Session` type or `None`.
    # Consequently, we then call the factory.
    if not isinstance(session, SpotifySession):
        session = session_factory(session)

    return session
