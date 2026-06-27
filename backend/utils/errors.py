"""
VirtualFit Pro — Error Handling & Response Utilities
======================================================
- Never expose stack traces
- Standardized JSON responses
- Custom exceptions
- Centralized error handler registration
"""

import logging
import traceback
from flask import jsonify, request

logger = logging.getLogger('virtualfit.app')


# ── Custom Exceptions ────────────────────────────────────

class VFError(Exception):
    """Base application error."""
    status_code = 500
    error_code = 'INTERNAL_ERROR'

    def __init__(self, message: str, status_code: int | None = None,
                 error_code: str | None = None):
        super().__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code


class ValidationError(VFError):
    status_code = 400
    error_code = 'VALIDATION_ERROR'


class AuthError(VFError):
    status_code = 401
    error_code = 'AUTH_ERROR'


class ForbiddenError(VFError):
    status_code = 403
    error_code = 'FORBIDDEN'


class NotFoundError(VFError):
    status_code = 404
    error_code = 'NOT_FOUND'


class RateLimitError(VFError):
    status_code = 429
    error_code = 'RATE_LIMITED'


class ExternalServiceError(VFError):
    status_code = 502
    error_code = 'EXTERNAL_SERVICE_ERROR'


# ── Response Helpers ─────────────────────────────────────

def success(data: dict | None = None, message: str = 'OK',
            status_code: int = 200) -> tuple:
    """Standard success response."""
    body = {'success': True, 'message': message}
    if data:
        body.update(data)
    return jsonify(body), status_code


def error(message: str, status_code: int = 400,
          error_code: str = 'ERROR', details: dict | None = None) -> tuple:
    """Standard error response — never exposes internal details."""
    body = {
        'success': False,
        'error': message,
        'code': error_code,
    }
    if details:
        body['details'] = details
    return jsonify(body), status_code


# ── Error Handler Registration ───────────────────────────

def register_error_handlers(app):
    """Register all Flask error handlers."""

    @app.errorhandler(VFError)
    def handle_vf_error(e):
        logger.warning(f"[VFError] {type(e).__name__}: {e.message} | {request.path}")
        return error(e.message, e.status_code, e.error_code)

    @app.errorhandler(400)
    def handle_400(e):
        return error('Bad request', 400, 'BAD_REQUEST')

    @app.errorhandler(401)
    def handle_401(e):
        return error('Authentication required', 401, 'UNAUTHORIZED')

    @app.errorhandler(403)
    def handle_403(e):
        return error('Access denied', 403, 'FORBIDDEN')

    @app.errorhandler(404)
    def handle_404(e):
        return error('Resource not found', 404, 'NOT_FOUND')

    @app.errorhandler(405)
    def handle_405(e):
        return error('Method not allowed', 405, 'METHOD_NOT_ALLOWED')

    @app.errorhandler(413)
    def handle_413(e):
        return error('File too large (max 16 MB)', 413, 'FILE_TOO_LARGE')

    @app.errorhandler(429)
    def handle_429(e):
        return error('Too many requests. Please slow down.', 429, 'RATE_LIMITED')

    @app.errorhandler(500)
    def handle_500(e):
        # Log full traceback internally, never expose to client
        logger.error(f"[500] {request.path}: {traceback.format_exc()}")
        return error('An internal error occurred. Please try again.', 500, 'INTERNAL_ERROR')

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Catch-all: log but don't expose
        logger.error(f"[Unhandled] {type(e).__name__}: {e} | {request.path}")
        logger.debug(traceback.format_exc())
        return error('An unexpected error occurred.', 500, 'INTERNAL_ERROR')
