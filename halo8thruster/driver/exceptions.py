class PPUError(Exception):
    """Base exception for all driver errors."""

class ConnectionError(PPUError):
    """Raised when the initial connection to the device fails."""

class CommsError(PPUError):
    """Raised on any SDO transport failure."""

class CommsTimeout(CommsError):
    """Raised when the device does not respond within the SDO timeout."""

class CommsAbort(CommsError):
    """Raised when the device explicitly rejects an SDO request."""

class StateError(PPUError):
    """Raised for state machine level errors (invalid value, bad transition)."""

class StateTimeout(StateError):
    """Raised when thruster_state_wait times out before reaching the desired state."""
