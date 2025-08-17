"""
Application-specific exceptions.
"""


class LockAcquisitionError(Exception):
    """Raised when acquiring a lock for a task fails."""

    pass
