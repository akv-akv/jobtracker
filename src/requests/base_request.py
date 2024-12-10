class InvalidRequest:
    """Base class for invalid requests."""

    def __init__(self):
        self.errors = []

    def add_error(self, parameter, message):
        self.errors.append({"parameter": parameter, "message": message})

    def has_errors(self):
        return len(self.errors) > 0

    def __bool__(self):
        return False


class ValidRequest:
    """Base class for valid requests."""

    def __init__(self, filters=None):
        self.filters = filters

    def __bool__(self):
        return True
