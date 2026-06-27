"""
VirtualFit Pro — Logging Configuration
========================================
Structured logging for:
- Application events
- Security events
- API calls
- Payment events
- Authentication events
"""

import os
import logging
import logging.handlers
from datetime import datetime


def setup_logging(app):
    """Configure all application loggers."""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    fmt = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    def _file_handler(filename: str, level=logging.DEBUG) -> logging.Handler:
        path = os.path.join(log_dir, filename)
        h = logging.handlers.RotatingFileHandler(
            path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
        )
        h.setFormatter(fmt)
        h.setLevel(level)
        return h

    def _console_handler() -> logging.Handler:
        h = logging.StreamHandler()
        h.setFormatter(fmt)
        h.setLevel(logging.DEBUG if app.debug else logging.WARNING)
        return h

    # ── Configure each named logger ───────────────────────
    loggers = {
        'virtualfit.app':      ('app.log',      level),
        'virtualfit.security': ('security.log', logging.WARNING),
        'virtualfit.api':      ('api.log',      logging.INFO),
        'virtualfit.payment':  ('payment.log',  logging.INFO),
        'virtualfit.auth':     ('auth.log',     logging.INFO),
        'virtualfit.ai':       ('ai.log',       logging.INFO),
    }

    for logger_name, (filename, log_level) in loggers.items():
        lg = logging.getLogger(logger_name)
        lg.setLevel(log_level)
        lg.addHandler(_file_handler(filename, log_level))
        if app.debug:
            lg.addHandler(_console_handler())
        lg.propagate = False

    # ── Flask's own logger ────────────────────────────────
    app.logger.setLevel(level)
    app.logger.addHandler(_file_handler('app.log', level))
    if app.debug:
        app.logger.addHandler(_console_handler())

    app.logger.info("✅ Logging initialized")
