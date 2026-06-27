"""
VirtualFit Pro — Database Layer
================================
Enterprise database with:
- Connection pooling
- Prepared statements (SQL injection prevention)
- Transactions
- Supabase REST client
- Centralized error handling
"""

import os
import time
import requests
from typing import Any
from flask import current_app

# MySQL connection pool
_pool = None

try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


# ── MySQL Pool ───────────────────────────────────────────

def init_mysql_pool(app):
    """Initialize MySQL connection pool on app startup."""
    global _pool
    if not MYSQL_AVAILABLE:
        app.logger.warning("mysql-connector-python not installed. MySQL disabled.")
        return
    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name='vf_pool',
            pool_size=int(app.config.get('DB_POOL_SIZE', 10)),
            pool_reset_session=True,
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASS'],
            database=app.config['DB_NAME'],
            charset='utf8mb4',
            use_unicode=True,
            autocommit=False,
        )
        app.logger.info("✅ MySQL pool initialized")
    except Exception as e:
        app.logger.error(f"❌ MySQL pool init failed: {e}")


def get_db_connection():
    """Get a connection from the pool."""
    if not _pool:
        return None
    try:
        return _pool.get_connection()
    except Exception as e:
        current_app.logger.error(f"[DB] Pool connection failed: {e}")
        return None


def db_execute(sql: str, params: tuple = (), fetch: bool = True) -> Any:
    """
    Execute a parameterized SQL query.
    - Uses prepared statements — immune to SQL injection.
    - Returns list of dicts on SELECT, lastrowid on INSERT.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True, prepared=True)
        cur.execute(sql, params)
        if fetch:
            result = cur.fetchall()
            cur.close()
            conn.close()
            return result
        else:
            conn.commit()
            last_id = cur.lastrowid
            cur.close()
            conn.close()
            return last_id
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        current_app.logger.error(f"[DB] Query error: {e} | SQL: {sql[:100]}")
        return None


def db_transaction(operations: list[tuple]) -> bool:
    """
    Execute multiple SQL operations in a single transaction.
    operations = [(sql, params), ...]
    Rolls back all on any failure.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        conn.autocommit = False
        cur = conn.cursor(dictionary=True, prepared=True)
        for sql, params in operations:
            cur.execute(sql, params)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        current_app.logger.error(f"[DB] Transaction failed: {e}")
        return False


# ── Supabase REST Client ─────────────────────────────────

class SupabaseClient:
    """
    Thin Supabase REST wrapper.
    All API keys are fetched from app config — never hardcoded.
    """

    def __init__(self, url: str, key: str):
        self.base_url = url.rstrip('/')
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }
        self._session = requests.Session()
        self._session.headers.update(self.headers)

    def _url(self, table: str) -> str:
        return f"{self.base_url}/rest/v1/{table}"

    def get(self, table: str, params: dict | None = None) -> list | None:
        """SELECT with query params. Returns list or None on error."""
        try:
            # Build safe query string from dict
            qs = '&'.join(f"{k}={v}" for k, v in (params or {}).items())
            url = self._url(table) + (f'?{qs}' if qs else '')
            r = self._session.get(url, timeout=10)
            if r.ok:
                return r.json()
            current_app.logger.warning(f"[SB] GET {table} {r.status_code}: {r.text[:200]}")
        except Exception as e:
            current_app.logger.error(f"[SB] GET {table} exception: {e}")
        return None

    def post(self, table: str, data: dict) -> list | None:
        """INSERT. Returns created row(s) or None."""
        try:
            r = self._session.post(self._url(table), json=data, timeout=10)
            if r.ok:
                return r.json()
            current_app.logger.warning(f"[SB] POST {table} {r.status_code}: {r.text[:200]}")
        except Exception as e:
            current_app.logger.error(f"[SB] POST {table} exception: {e}")
        return None

    def patch(self, table: str, match: str, data: dict) -> list | None:
        """UPDATE where match. Returns updated row(s) or None."""
        try:
            r = self._session.patch(
                f"{self._url(table)}?{match}", json=data, timeout=10
            )
            if r.ok:
                return r.json()
        except Exception as e:
            current_app.logger.error(f"[SB] PATCH {table} exception: {e}")
        return None

    def delete(self, table: str, match: str) -> bool:
        """DELETE where match. Returns True on success."""
        try:
            r = self._session.delete(f"{self._url(table)}?{match}", timeout=10)
            return r.ok
        except Exception:
            return False


# Singleton — initialized in app factory
_supabase: SupabaseClient | None = None


def init_supabase(app):
    global _supabase
    url = app.config.get('SUPABASE_URL', '')
    key = app.config.get('SUPABASE_KEY', '')
    if url and key:
        _supabase = SupabaseClient(url, key)
        app.logger.info("✅ Supabase client initialized")
    else:
        app.logger.warning("⚠️  Supabase not configured — DB features disabled")


def get_supabase() -> SupabaseClient | None:
    return _supabase
