"""Like-related exceptions."""


class LikeNotFoundException(Exception):
    """Raised when a like is not found."""
    pass


class LikeAlreadyExistsException(Exception):
    """Raised when trying to create a like that already exists."""
    pass


class InvalidLikeDataException(Exception):
    """Raised when like data is invalid."""
    pass