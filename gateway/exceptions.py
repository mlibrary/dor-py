class NoContentError(Exception):
    pass

class RepositoryGatewayError(Exception):
    pass

class NoStagedChangesError(RepositoryGatewayError):
    pass

class ObjectDoesNotExistError(RepositoryGatewayError):
    pass

class StagedObjectAlreadyExistsError(RepositoryGatewayError):
    pass

class StagedObjectDoesNotExistError(RepositoryGatewayError):
    pass
