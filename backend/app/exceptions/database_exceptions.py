class DatabaseException(Exception):
    def __init__(self, message: str, operation: str = None, error: Exception = None):
        self.message = message
        self.operation = operation
        self.original_error = error
        super().__init__(self.message)

class ConnectionException(DatabaseException):
    pass

class QueryException(DatabaseException):
    pass

class DocumentNotFoundException(DatabaseException):
    pass
