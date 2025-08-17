"""Movie-related exceptions."""


class MovieNotFoundException(Exception):
    """Raised when a movie is not found."""
    pass


class MovieAlreadyExistsException(Exception):
    """Raised when trying to create a movie that already exists."""
    pass


class InvalidMovieDataException(Exception):
    """Raised when movie data is invalid."""
    pass