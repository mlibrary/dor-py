class RepositoryGatewayError(Exception):
    pass

class NoStagedChangesError(RepositoryGatewayError):
    pass

class ObjectDoesNotExistError(RepositoryGatewayError):
    pass

class StagedObjectAlreadyExistsError(RepositoryGatewayError):
    pass

class ObjectAlreadyExistsError(RepositoryGatewayError):
    pass