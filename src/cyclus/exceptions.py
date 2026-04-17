"""Exceptions for the Cyclus library."""


class CyclusError(Exception):
    """Base exception for Cyclus errors."""


class CyclusAuthenticationError(CyclusError):
    """Raised when authentication with the Cyclus API fails."""
