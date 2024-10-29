class ApplicationException(Exception):
    pass

class NoContentException(ApplicationException):
    pass

class ObjectDoesNotExistException(ApplicationException):
    pass

class ObjectAlreadyExistsException(ApplicationException):
    pass

class ObjectNotStagedException(ApplicationException):
    pass
