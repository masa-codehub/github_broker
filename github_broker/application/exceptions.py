class ApplicationError(Exception):
    """Base class for application-specific errors."""
    pass

class LockAcquisitionError(ApplicationError):
    """Raised when a lock for a task cannot be acquired."""
    pass