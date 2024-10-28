class ApplicationException(Exception):
    pass

class NoContentException(ApplicationException):
    pass

class ObjectDoesNotExistException(ApplicationException):
    pass
