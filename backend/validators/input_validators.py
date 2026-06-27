"""
VirtualFit Pro — Input Validators
===================================
Centralized validation for all request inputs.
Never trust frontend data.
"""

import re
import base64
import imghdr
from typing import Any


# ── Regex Patterns ───────────────────────────────────────

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
PHONE_RE = re.compile(r'^\+?[\d\s\-]{7,20}$')
NAME_RE = re.compile(r'^[a-zA-Z\s\'\-\.]{2,100}$')
ORDER_NUM_RE = re.compile(r'^VF\d{8}$')


# ── Validation Helpers ───────────────────────────────────

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(str(email).strip().lower()))


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(str(phone).strip()))


def is_valid_name(name: str) -> bool:
    return bool(NAME_RE.match(str(name).strip()))


def is_valid_password(password: str) -> tuple[bool, str]:
    """
    Password must be:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    p = str(password)
    if len(p) < 8:
        return False, 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', p):
        return False, 'Password must contain an uppercase letter'
    if not re.search(r'[a-z]', p):
        return False, 'Password must contain a lowercase letter'
    if not re.search(r'\d', p):
        return False, 'Password must contain a digit'
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', p):
        return False, 'Password must contain a special character'
    return True, ''


def is_valid_amount(amount: Any) -> bool:
    try:
        v = float(amount)
        return 0 < v <= 9_999_999
    except (TypeError, ValueError):
        return False


def is_valid_gender(gender: str) -> bool:
    return gender in ('men', 'women', 'boys', 'girls', 'mid-age')


def is_valid_category(cat: str) -> bool:
    return cat in ('upper_body', 'lower_body', 'dresses', 'full_body', 'tops',
                   'bottoms', 'one-pieces', 'auto')


# ── Image Validation ─────────────────────────────────────

ALLOWED_IMAGE_HEADERS = {
    b'\xff\xd8\xff': 'jpeg',  # JPEG
    b'\x89PNG':       'png',  # PNG
    b'RIFF':          'webp', # WEBP (also check bytes 8-12)
    b'GIF8':          'gif',  # GIF (reject in practice)
}

MAX_IMAGE_B64_LEN = 14 * 1024 * 1024  # ~10MB decoded


def validate_base64_image(b64_string: str) -> tuple[bool, str]:
    """
    Validate a base64-encoded image.
    Checks:
    1. Not empty
    2. Strip data URL prefix
    3. Size limit
    4. Valid base64
    5. Magic byte check (MIME type validation)
    6. Not SVG/HTML (XSS vectors)
    """
    if not b64_string:
        return False, 'No image provided'

    # Strip data URL prefix  e.g. "data:image/jpeg;base64,"
    if ',' in b64_string:
        header, b64_string = b64_string.split(',', 1)
        # Block SVG/HTML disguised as images
        if 'svg' in header.lower() or 'html' in header.lower():
            return False, 'SVG and HTML uploads are not allowed'

    b64_string = b64_string.strip().replace('\n', '').replace('\r', '').replace(' ', '')

    if not b64_string:
        return False, 'Empty image data'

    if len(b64_string) > MAX_IMAGE_B64_LEN:
        return False, 'Image too large (max 10 MB)'

    # Validate base64 encoding
    try:
        decoded = base64.b64decode(b64_string, validate=True)
    except Exception:
        return False, 'Invalid base64 encoding'

    if len(decoded) < 10:
        return False, 'Image data too small'

    # Magic byte check — verify actual image format
    magic = decoded[:4]
    allowed = False
    for header_bytes, fmt in ALLOWED_IMAGE_HEADERS.items():
        if magic[:len(header_bytes)] == header_bytes:
            if fmt == 'webp':
                # RIFF....WEBP
                if decoded[8:12] == b'WEBP':
                    allowed = True
                    break
            elif fmt == 'gif':
                pass  # We block GIF
            else:
                allowed = True
                break

    if not allowed:
        return False, 'Only JPEG, PNG, and WebP images are allowed'

    return True, 'ok'


# ── Registration Validator ───────────────────────────────

def validate_registration(data: dict) -> tuple[bool, dict]:
    """
    Validate user registration payload.
    Returns (is_valid, errors_dict).
    """
    errors = {}

    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    phone = str(data.get('phone', '')).strip()
    gender = str(data.get('gender', '')).strip()

    if not is_valid_name(name):
        errors['name'] = 'Name must be 2-100 characters (letters and spaces only)'

    if not is_valid_email(email):
        errors['email'] = 'Invalid email address'

    pwd_ok, pwd_msg = is_valid_password(password)
    if not pwd_ok:
        errors['password'] = pwd_msg

    if phone and not is_valid_phone(phone):
        errors['phone'] = 'Invalid phone number'

    if gender and not is_valid_gender(gender):
        errors['gender'] = 'Invalid gender value'

    return len(errors) == 0, errors


def validate_login(data: dict) -> tuple[bool, dict]:
    errors = {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not is_valid_email(email):
        errors['email'] = 'Invalid email address'
    if not password:
        errors['password'] = 'Password required'

    return len(errors) == 0, errors


def validate_checkout(data: dict) -> tuple[bool, dict]:
    errors = {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    phone = str(data.get('phone', '')).strip()
    address = str(data.get('address', '')).strip()
    total = data.get('total', 0)

    if not is_valid_name(name):
        errors['name'] = 'Valid name required'
    if not is_valid_email(email):
        errors['email'] = 'Valid email required'
    if not is_valid_phone(phone):
        errors['phone'] = 'Valid phone number required'
    if not address or len(address) < 5:
        errors['address'] = 'Valid address required'
    if not is_valid_amount(total):
        errors['total'] = 'Invalid order amount'

    items = data.get('items', [])
    if not items or not isinstance(items, list):
        errors['items'] = 'Order must contain at least one item'

    return len(errors) == 0, errors


def sanitize_string(value, max_length: int = 500) -> str:
    """Sanitize string input."""
    import html
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    value = value.replace("\x00", "").strip()[:max_length]
    return value

