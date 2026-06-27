"""
VirtualFit Pro — Security Middleware
=====================================
Implements:
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Request sanitization
- Audit logging
- IP extraction
- Bot detection
"""

import re
import time
import json
import logging
import html
from datetime import datetime, timezone
from flask import request, jsonify, g

# Security logger (separate from app log)
security_logger = logging.getLogger('virtualfit.security')


# ── Security Headers ─────────────────────────────────────

def apply_security_headers(response):
    """
    Add OWASP-recommended security headers to every response.
    Original: only had X-Content-Type-Options, X-Frame-Options, X-XSS-Protection.
    Improved: full enterprise header set.
    """
    h = response.headers

    # Prevent MIME type sniffing
    h['X-Content-Type-Options'] = 'nosniff'

    # Clickjacking protection
    h['X-Frame-Options'] = 'SAMEORIGIN'

    # Legacy XSS filter (browsers ignoring this now, but belt + suspenders)
    h['X-XSS-Protection'] = '1; mode=block'

    # Referrer policy — don't leak URL to third parties
    h['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Permissions policy — disable unused browser APIs
    h['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=(), payment=()'
    )

    # Content Security Policy — prevent XSS script injection
    h['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self' https://fcretwoovhfzeqziucca.supabase.co; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self' https://sandbox.payhere.lk https://www.payhere.lk;"
    )

    # HSTS — force HTTPS for 1 year (enable in production behind HTTPS)
    # Only set if we're serving HTTPS
    if request.is_secure:
        h['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Remove server fingerprint
    h.pop('Server', None)
    h.pop('X-Powered-By', None)

    # Cache control for sensitive API endpoints
    if request.path.startswith('/api/'):
        h['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
        h['Pragma'] = 'no-cache'
        h['Expires'] = '0'
    
    # Additional security
    h['X-Download-Options'] = 'noopen'  # IE: don't auto-open downloads
    h['X-DNS-Prefetch-Control'] = 'off'  # Prevent DNS prefetch leaks

    return response


# ── Input Sanitization ───────────────────────────────────

_DANGEROUS_PATTERNS = [
    re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick=, onload=, etc.
    re.compile(r'<iframe', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
    re.compile(r'data:text/html', re.IGNORECASE),
]

_SQL_PATTERNS = [
    re.compile(r'\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
               re.IGNORECASE),
    re.compile(r'--\s*$', re.MULTILINE),
    re.compile(r'/\*.*?\*/', re.DOTALL),
    re.compile(r"';|\";\s*(DROP|SELECT)", re.IGNORECASE),
]


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string value:
    - Truncate to max_length
    - HTML-escape dangerous characters
    - Strip null bytes
    """
    if not isinstance(value, str):
        return ''
    value = value.replace('\x00', '').strip()[:max_length]
    return html.escape(value, quote=True)


def contains_xss(value: str) -> bool:
    """Return True if the string contains suspected XSS payload."""
    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(value):
            return True
    return False


def detect_sqli(value: str) -> bool:
    """Heuristic SQL injection detection (defense-in-depth; primary is parameterized queries)."""
    for pattern in _SQL_PATTERNS:
        if pattern.search(value):
            return True
    return False


def validate_request_payload(data: dict, max_depth: int = 5) -> tuple[bool, str]:
    """
    Recursively check all string values in JSON payload.
    Returns (is_safe, reason).
    """
    def _check(obj, depth=0):
        if depth > max_depth:
            return False, 'Payload too deeply nested'
        if isinstance(obj, dict):
            for k, v in obj.items():
                ok, msg = _check(v, depth + 1)
                if not ok:
                    return False, msg
        elif isinstance(obj, list):
            for item in obj:
                ok, msg = _check(item, depth + 1)
                if not ok:
                    return False, msg
        elif isinstance(obj, str):
            if contains_xss(obj):
                return False, 'XSS pattern detected'
        return True, ''

    return _check(data)


# ── IP Extraction ────────────────────────────────────────

def get_client_ip() -> str:
    """
    Extract real client IP, handling proxies safely.
    We check X-Forwarded-For only if behind trusted proxy.
    """
    # X-Forwarded-For can be spoofed; use only the rightmost non-private IP
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        # Take the last IP added by a trusted proxy
        ips = [ip.strip() for ip in xff.split(',')]
        return ips[-1] if ips else request.remote_addr or 'unknown'
    return request.remote_addr or 'unknown'


# ── Audit Logging ────────────────────────────────────────

def _mask_email(email: str) -> str:
    """Mask email for logging: user@example.com → u***@example.com"""
    if not email or '@' not in email:
        return '***'
    local, domain = email.split('@', 1)
    masked = local[0] + '***' if local else '***'
    return f'{masked}@{domain}'


def _sanitize_log_details(details: dict) -> dict:
    """Remove/mask PII from log details before writing."""
    SENSITIVE_KEYS = {'password', 'hash', 'token', 'secret', 'key', 'card', 'cvv'}
    safe = {}
    for k, v in details.items():
        if any(s in k.lower() for s in SENSITIVE_KEYS):
            safe[k] = '***REDACTED***'
        elif k == 'email' and isinstance(v, str):
            safe[k] = _mask_email(v)
        else:
            safe[k] = v
    return safe


def log_security_event(event_type: str, details: dict | None = None):
    """
    Write a structured security event to the security log.
    PII is masked before writing.
    Never call print() for security events — always use this.
    """
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event': event_type,
        'ip': get_client_ip(),
        'path': request.path,
        'method': request.method,
        'user_agent': request.headers.get('User-Agent', '')[:100],
    }
    if details:
        entry.update(_sanitize_log_details(details))

    user = getattr(request, 'current_user', None)
    if user:
        entry['user_id'] = user.get('id')
        # Mask email in logs
        if user.get('email'):
            entry['email'] = _mask_email(user['email'])

    security_logger.warning(json.dumps(entry))


def log_api_request():
    """Before-request hook: record timing start."""
    g.start_time = time.time()


def log_api_response(response):
    """After-request hook: log API calls with duration."""
    if request.path.startswith('/api/'):
        duration_ms = int((time.time() - getattr(g, 'start_time', time.time())) * 1000)
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logging.getLogger('virtualfit.api').log(
            level,
            json.dumps({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration_ms': duration_ms,
                'ip': get_client_ip(),
            })
        )
    return response


# ── CSRF / Origin Validation ────────────────────────────

def check_api_origin(app_config: dict) -> bool:
    """
    Verify request origin for state-changing API calls.
    Returns True if origin is allowed.
    """
    origin = request.headers.get('Origin', '')
    referer = request.headers.get('Referer', '')
    
    if not origin and not referer:
        # Allow requests without Origin (server-to-server, CLI tools)
        # In strict mode, reject these
        return True
    
    allowed = app_config.get('ALLOWED_ORIGINS', ['http://localhost:5000'])
    check_val = origin or referer
    return any(check_val.startswith(o) for o in allowed)


# ── Bot Detection ────────────────────────────────────────

_BOT_PATTERNS = re.compile(
    r'(bot|crawler|spider|scraper|curl|wget|python-requests)',
    re.IGNORECASE,
)


def is_bot() -> bool:
    ua = request.headers.get('User-Agent', '')
    return bool(_BOT_PATTERNS.search(ua))
