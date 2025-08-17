class AuthException(Exception):
    pass


class EmailAlreadyExistsException(AuthException):
    pass


class UsernameAlreadyExistsException(AuthException):
    pass


class InvalidCredentialsException(AuthException):
    pass


class UserInactiveException(AuthException):
    pass


class InvalidTokenException(AuthException):
    pass
