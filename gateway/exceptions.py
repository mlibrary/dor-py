class NoContentError(Exception):
    pass

class RepositoryGatewayError(Exception):
    pass

class ObjectDoesNotExistError(RepositoryGatewayError):
    pass

class ObjectAlreadyExistsError(RepositoryGatewayError):
    pass

class ObjectNotStagedError(RepositoryGatewayError):
    pass
