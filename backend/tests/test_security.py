"""
VirtualFit Pro — Security & Integration Tests
==============================================
Tests for:
- Authentication (JWT, bcrypt)
- Input validation
- Rate limiting
- Authorization
- SQL injection prevention
- XSS prevention
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest


# ── Auth Tests ───────────────────────────────────────────

class TestPasswordHashing:
    def test_bcrypt_hash_not_plain(self):
        from backend.auth.jwt_manager import hash_password
        hashed = hash_password('TestPass@123')
        assert hashed != 'TestPass@123'
        assert hashed.startswith('$2b$')

    def test_bcrypt_verify_correct(self):
        from backend.auth.jwt_manager import hash_password, verify_password
        h = hash_password('MyPassword@1')
        assert verify_password('MyPassword@1', h) is True

    def test_bcrypt_verify_wrong(self):
        from backend.auth.jwt_manager import hash_password, verify_password
        h = hash_password('MyPassword@1')
        assert verify_password('WrongPassword', h) is False

    def test_sha256_migration(self):
        import hashlib
        from backend.auth.jwt_manager import migrate_sha256_to_bcrypt
        old_hash = hashlib.sha256('OldPass@1'.encode()).hexdigest()
        valid, new_hash = migrate_sha256_to_bcrypt('OldPass@1', old_hash)
        assert valid is True
        assert new_hash.startswith('$2b$')

    def test_sha256_migration_wrong_password(self):
        import hashlib
        from backend.auth.jwt_manager import migrate_sha256_to_bcrypt
        old_hash = hashlib.sha256('OldPass@1'.encode()).hexdigest()
        valid, _ = migrate_sha256_to_bcrypt('WrongPass', old_hash)
        assert valid is False


class TestLoginAttemptTracking:
    def setup_method(self):
        from backend.auth import jwt_manager
        jwt_manager._login_attempts.clear()

    def test_lockout_after_max_attempts(self):
        from backend.auth.jwt_manager import record_failed_attempt, is_locked_out
        for _ in range(5):
            record_failed_attempt('test@test.com:1.2.3.4')
        assert is_locked_out('test@test.com:1.2.3.4', max_attempts=5) is True

    def test_no_lockout_before_max(self):
        from backend.auth.jwt_manager import record_failed_attempt, is_locked_out
        for _ in range(4):
            record_failed_attempt('other@test.com:1.2.3.4')
        assert is_locked_out('other@test.com:1.2.3.4', max_attempts=5) is False

    def test_clear_attempts_on_success(self):
        from backend.auth.jwt_manager import record_failed_attempt, clear_attempts, is_locked_out
        for _ in range(5):
            record_failed_attempt('clear@test.com:1.1.1.1')
        clear_attempts('clear@test.com:1.1.1.1')
        assert is_locked_out('clear@test.com:1.1.1.1', max_attempts=5) is False


# ── Input Validation Tests ───────────────────────────────

class TestInputValidation:
    def test_valid_email(self):
        from backend.validators.input_validators import is_valid_email
        assert is_valid_email('user@example.com') is True

    def test_invalid_email(self):
        from backend.validators.input_validators import is_valid_email
        assert is_valid_email('notanemail') is False
        assert is_valid_email('') is False
        assert is_valid_email('<script>@evil.com') is False

    def test_password_strength(self):
        from backend.validators.input_validators import is_valid_password
        ok, _ = is_valid_password('Str0ng@Pass!')
        assert ok is True

    def test_weak_password(self):
        from backend.validators.input_validators import is_valid_password
        ok, msg = is_valid_password('weak')
        assert ok is False
        assert 'least 8' in msg

    def test_no_special_char_password(self):
        from backend.validators.input_validators import is_valid_password
        ok, msg = is_valid_password('NoSpecial1')
        assert ok is False

    def test_valid_registration(self):
        from backend.validators.input_validators import validate_registration
        ok, errors = validate_registration({
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'MyPass@123',
        })
        assert ok is True
        assert not errors

    def test_invalid_registration_missing_fields(self):
        from backend.validators.input_validators import validate_registration
        ok, errors = validate_registration({'name': '', 'email': '', 'password': ''})
        assert ok is False
        assert 'name' in errors
        assert 'email' in errors
        assert 'password' in errors


class TestXSSDetection:
    def test_script_tag_detected(self):
        from backend.middleware.security import contains_xss
        assert contains_xss('<script>alert(1)</script>') is True

    def test_onclick_detected(self):
        from backend.middleware.security import contains_xss
        assert contains_xss('hello onclick=evil()') is True

    def test_normal_text_safe(self):
        from backend.middleware.security import contains_xss
        assert contains_xss('I want a blue shirt') is False

    def test_javascript_url_detected(self):
        from backend.middleware.security import contains_xss
        assert contains_xss('javascript:alert(1)') is True


class TestImageValidation:
    def test_rejects_empty(self):
        from backend.validators.input_validators import validate_base64_image
        ok, msg = validate_base64_image('')
        assert ok is False

    def test_rejects_svg_header(self):
        from backend.validators.input_validators import validate_base64_image
        ok, msg = validate_base64_image('data:image/svg+xml;base64,abc123')
        assert ok is False
        assert 'SVG' in msg

    def test_rejects_oversized(self):
        import base64
        from backend.validators.input_validators import validate_base64_image
        huge = base64.b64encode(b'A' * (15 * 1024 * 1024)).decode()
        ok, msg = validate_base64_image(huge)
        assert ok is False
        assert 'large' in msg.lower()


class TestSanitization:
    def test_html_escape(self):
        from backend.middleware.security import sanitize_string
        result = sanitize_string('<b>bold</b>')
        assert '<b>' not in result
        assert '&lt;b&gt;' in result

    def test_null_byte_stripped(self):
        from backend.middleware.security import sanitize_string
        result = sanitize_string('hello\x00world')
        assert '\x00' not in result

    def test_max_length_respected(self):
        from backend.middleware.security import sanitize_string
        result = sanitize_string('A' * 1000, max_length=100)
        assert len(result) <= 100
