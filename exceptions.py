class TravelnestException(Exception):
    """Base exception"""


class FieldNotFound(TravelnestException):
    pass


class MultipleFieldMatches(TravelnestException):
    pass