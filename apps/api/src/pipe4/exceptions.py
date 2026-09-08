from __future__ import annotations


class Pipe4Error(Exception):
    code = "PIPE4_ERROR"
    status_code = 400

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFound(Pipe4Error):
    code = "RESOURCE_NOT_FOUND"
    status_code = 404


class PermissionDenied(Pipe4Error):
    code = "FORBIDDEN"
    status_code = 403


class AuthenticationRequired(Pipe4Error):
    code = "AUTHENTICATION_REQUIRED"
    status_code = 401


class Conflict(Pipe4Error):
    code = "CONFLICT"
    status_code = 409


class InvalidTransition(Conflict):
    code = "INVALID_STATE_TRANSITION"


class PolicyConfigurationError(Pipe4Error):
    code = "POLICY_CONFIGURATION_ERROR"
    status_code = 500


class ExternalDependencyUnavailable(Pipe4Error):
    code = "DEPENDENCY_UNAVAILABLE"
    status_code = 503


class RateLimited(Pipe4Error):
    code = "RATE_LIMITED"
    status_code = 429
