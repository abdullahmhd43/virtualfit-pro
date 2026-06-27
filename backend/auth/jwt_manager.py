"""
VirtualFit Pro — JWT Authentication Service
=============================================
Enterprise-grade JWT with:
- Access tokens (15 min)
- Refresh tokens (7 days)
- Secure bcrypt password hashing
- Login attempt tracking
- Account lockout
- Role-based access control
"""

import jwt
import bcrypt
import hashlib
import secrets
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify, current_app

# In-memory store for login attempts (use Redis in production)
_login_attempts: dict = {}
_refresh_tokens: set = set()  # blacklisted refresh tokens


# ── Password Hashing ─────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash password with bcrypt. Never store plain text."""
    rounds = int(os.environ.get('BCRYPT_ROUNDS', 12))
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(rounds)).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time password comparison to prevent timing attacks."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def migrate_sha256_to_bcrypt(plain: str, old_hash: str) -> tuple[bool, str]:
    """
    Migrate legacy SHA-256 hashes to bcrypt on first login.
    Returns (is_valid, new_bcrypt_hash_or_empty).
    """
    sha = hashlib.sha256(plain.encode()).hexdigest()
    if secrets.compare_digest(sha, old_hash):
        return True, hash_password(plain)
    return False, ''


# ── Token Generation ─────────────────────────────────────

def generate_access_token(user_id: int, email: str, role: str) -> str:
    """Generate short-lived access JWT (default 15 min)."""
    cfg = current_app.config
    payload = {
        'sub': str(user_id),
        'email': email,
        'role': role,
        'type': 'access',
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + cfg.get(
            'JWT_ACCESS_TOKEN_EXPIRES', timedelta(seconds=900)
        ),
        'jti': secrets.token_hex(16),
    }
    return jwt.encode(payload, cfg['JWT_SECRET_KEY'], algorithm='HS256')


def generate_refresh_token(user_id: int) -> str:
    """Generate long-lived refresh JWT (default 7 days)."""
    cfg = current_app.config
    payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + cfg.get(
            'JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=7)
        ),
        'jti': secrets.token_hex(16),
    }
    return jwt.encode(payload, cfg['JWT_SECRET_KEY'], algorithm='HS256')


def decode_token(token: str) -> dict:
    """Decode and validate JWT. Raises jwt.InvalidTokenError on failure."""
    return jwt.decode(
        token,
        current_app.config['JWT_SECRET_KEY'],
        algorithms=['HS256'],
    )


def blacklist_refresh_token(jti: str):
    """Mark a refresh token as revoked (logout)."""
    _refresh_tokens.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    return jti in _refresh_tokens


# ── Login Attempt Tracking ───────────────────────────────

def record_failed_attempt(identifier: str):
    """Track failed login attempts per email/IP."""
    now = time.time()
    if identifier not in _login_attempts:
        _login_attempts[identifier] = []
    _login_attempts[identifier].append(now)
    # Keep only attempts in the last 15 minutes
    _login_attempts[identifier] = [
        t for t in _login_attempts[identifier] if now - t < 900
    ]


def is_locked_out(identifier: str, max_attempts: int = 5) -> bool:
    """Return True if identifier has exceeded max login attempts."""
    attempts = _login_attempts.get(identifier, [])
    now = time.time()
    recent = [t for t in attempts if now - t < 900]
    return len(recent) >= max_attempts


def clear_attempts(identifier: str):
    """Clear attempts on successful login."""
    _login_attempts.pop(identifier, None)


def remaining_attempts(identifier: str, max_attempts: int = 5) -> int:
    attempts = _login_attempts.get(identifier, [])
    now = time.time()
    recent = len([t for t in attempts if now - t < 900])
    return max(0, max_attempts - recent)


# ── Auth Decorators ──────────────────────────────────────

def _extract_token() -> str | None:
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    # Also accept from cookie (HttpOnly)
    return request.cookies.get('access_token')


def require_auth(f):
    """
    Decorator: require valid JWT access token.
    Sets request.current_user = {id, email, role}
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({'error': 'Authentication required', 'code': 'NO_TOKEN'}), 401
        try:
            payload = decode_token(token)
            if payload.get('type') != 'access':
                return jsonify({'error': 'Invalid token type', 'code': 'BAD_TOKEN'}), 401
            request.current_user = {
                'id': int(payload['sub']),
                'email': payload['email'],
                'role': payload['role'],
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired', 'code': 'TOKEN_EXPIRED'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token', 'code': 'INVALID_TOKEN'}), 401
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    """Decorator: require admin role (stacks on top of require_auth)."""
    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required', 'code': 'FORBIDDEN'}), 403
        return f(*args, **kwargs)
    return wrapper


def optional_auth(f):
    """Decorator: attach user if token present, but don't block if missing."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        request.current_user = None
        token = _extract_token()
        if token:
            try:
                payload = decode_token(token)
                if payload.get('type') == 'access':
                    request.current_user = {
                        'id': int(payload['sub']),
                        'email': payload['email'],
                        'role': payload['role'],
                    }
            except jwt.InvalidTokenError:
                pass
        return f(*args, **kwargs)
    return wrapper
