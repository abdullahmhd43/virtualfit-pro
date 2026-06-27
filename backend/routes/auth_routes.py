"""
VirtualFit Pro — Auth Routes Blueprint
========================================
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
"""

import logging
from flask import Blueprint, request, jsonify, make_response, current_app

from backend.auth.jwt_manager import (
    hash_password, verify_password, migrate_sha256_to_bcrypt,
    generate_access_token, generate_refresh_token,
    decode_token, blacklist_refresh_token,
    record_failed_attempt, is_locked_out, clear_attempts,
    remaining_attempts, require_auth,
)
from backend.database.connection import get_supabase
from backend.validators.input_validators import validate_registration, validate_login, is_valid_password
from backend.middleware.security import log_security_event, get_client_ip
from backend.utils.errors import error, success, ValidationError

import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger('virtualfit.auth')


# ── Register ─────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    is_valid, errors = validate_registration(data)
    if not is_valid:
        return error('Validation failed', 400, 'VALIDATION_ERROR', errors)

    email = data['email'].strip().lower()
    sb = get_supabase()
    if not sb:
        return error('Registration service unavailable. Please try again later.', 503, 'DB_ERROR')

    # Check duplicate email
    existing = sb.get('users', {'email': f'eq.{email}', 'select': 'id'})
    if existing is None:
        return error('Database connection failed. Please try again.', 503, 'DB_ERROR')
    if existing:
        log_security_event('REGISTER_DUPLICATE_EMAIL', {'email': email})
        return error('Email already registered', 409, 'EMAIL_EXISTS')

    pwd_hash = hash_password(data['password'])
    result = sb.post('users', {
        'name': data['name'].strip(),
        'email': email,
        'password': pwd_hash,
        'phone': data.get('phone', '').strip(),
        'gender': data.get('gender', 'men'),
        'role': 'customer',
        'is_active': True,
    })

    if not result:
        return error('Registration failed. Please try again.', 500, 'DB_ERROR')

    user = result[0]
    sb.post('analytics', {'event_type': 'register', 'user_id': user['id']})
    log_security_event('REGISTER_SUCCESS', {'user_id': user['id'], 'email': email})
    logger.info(f"New registration: {email} (id={user['id']})")

    return success({'user_id': user['id']}, 'Registration successful', 201)


# ── Login ────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    is_valid, errors = validate_login(data)
    if not is_valid:
        return error('Validation failed', 400, 'VALIDATION_ERROR', errors)

    email = data['email'].strip().lower()
    password = data['password']
    ip = get_client_ip()

    # Brute-force / lockout check
    lockout_key = f"{email}:{ip}"
    max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
    if is_locked_out(lockout_key, max_attempts):
        log_security_event('LOGIN_LOCKED_OUT', {'email': email})
        return error(
            'Account temporarily locked due to too many failed attempts. '
            'Please wait 15 minutes.',
            429, 'ACCOUNT_LOCKED'
        )

    sb = get_supabase()
    if not sb:
        return error('Database unavailable', 503, 'DB_ERROR')

    users = sb.get('users', {
        'email': f'eq.{email}',
        'is_active': 'eq.true',
        'select': 'id,name,email,role,gender,password',
    })

    # Generic message — never reveal if email exists
    INVALID_MSG = 'Invalid email or password'

    if not users:
        record_failed_attempt(lockout_key)
        log_security_event('LOGIN_USER_NOT_FOUND', {'email': email})
        return error(INVALID_MSG, 401, 'INVALID_CREDENTIALS')

    user = users[0]
    stored_hash = user.get('password', '')

    # Support bcrypt (new) and SHA-256 (legacy migration)
    verified = False
    new_hash = None

    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        # bcrypt
        verified = verify_password(password, stored_hash)
    else:
        # Legacy SHA-256 — migrate on success
        verified, new_hash = migrate_sha256_to_bcrypt(password, stored_hash)

    if not verified:
        record_failed_attempt(lockout_key)
        rem = remaining_attempts(lockout_key, max_attempts)
        log_security_event('LOGIN_FAILED', {'email': email, 'remaining': rem})
        msg = INVALID_MSG
        if rem <= 2:
            msg += f' ({rem} attempts remaining before lockout)'
        return error(msg, 401, 'INVALID_CREDENTIALS')

    # Upgrade legacy hash
    if new_hash:
        sb.patch('users', f'id=eq.{user["id"]}', {'password': new_hash})
        logger.info(f"[AUTH] Migrated SHA-256 → bcrypt for user {user['id']}")

    clear_attempts(lockout_key)
    sb.patch('users', f'id=eq.{user["id"]}', {'last_login': 'now()'})
    sb.post('analytics', {'event_type': 'login', 'user_id': user['id']})
    log_security_event('LOGIN_SUCCESS', {'user_id': user['id'], 'email': email})

    # Generate tokens
    access_token = generate_access_token(user['id'], user['email'], user['role'])
    refresh_token = generate_refresh_token(user['id'])

    user_data = {k: user[k] for k in ('id', 'name', 'email', 'role', 'gender')}

    resp = make_response(jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user_data,
        'access_token': access_token,
    }))

    # Set refresh token as HttpOnly cookie
    resp.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=not current_app.debug,
        samesite='Lax',
        max_age=7 * 24 * 3600,
        path='/api/auth',
    )
    return resp, 200


# ── Refresh ──────────────────────────────────────────────

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token') or \
                    (request.get_json(silent=True) or {}).get('refresh_token')

    if not refresh_token:
        return error('Refresh token required', 401, 'NO_REFRESH_TOKEN')

    try:
        payload = decode_token(refresh_token)
    except jwt.ExpiredSignatureError:
        return error('Refresh token expired. Please log in again.', 401, 'REFRESH_EXPIRED')
    except jwt.InvalidTokenError:
        return error('Invalid refresh token', 401, 'INVALID_REFRESH')

    if payload.get('type') != 'refresh':
        return error('Invalid token type', 401, 'BAD_TOKEN')

    jti = payload.get('jti', '')
    from backend.auth.jwt_manager import is_token_blacklisted
    if is_token_blacklisted(jti):
        log_security_event('REFRESH_BLACKLISTED_TOKEN', {'jti': jti})
        return error('Token has been revoked', 401, 'TOKEN_REVOKED')

    # Fetch user
    user_id = int(payload['sub'])
    sb = get_supabase()
    users = sb.get('users', {
        'id': f'eq.{user_id}',
        'is_active': 'eq.true',
        'select': 'id,email,role,gender',
    }) if sb else None

    if not users:
        return error('User not found', 401, 'USER_NOT_FOUND')

    user = users[0]
    new_access = generate_access_token(user['id'], user['email'], user['role'])
    return jsonify({'success': True, 'access_token': new_access}), 200


# ── Logout ───────────────────────────────────────────────

@auth_bp.route('/logout', methods=['POST'])
def logout():
    refresh_token = request.cookies.get('refresh_token')
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get('jti', '')
            if jti:
                blacklist_refresh_token(jti)
        except Exception:
            pass

    resp = make_response(jsonify({'success': True, 'message': 'Logged out'}))
    resp.delete_cookie('refresh_token', path='/api/auth')
    resp.delete_cookie('access_token')
    log_security_event('LOGOUT')
    return resp, 200


# ── Current User ─────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    user_id = request.current_user['id']
    sb = get_supabase()
    users = sb.get('users', {
        'id': f'eq.{user_id}',
        'select': 'id,name,email,role,gender,phone,created_at,last_login',
    }) if sb else None

    if not users:
        return error('User not found', 404, 'NOT_FOUND')

    u = users[0]
    u.pop('password', None)  # Never return password hash
    return success({'user': u})
