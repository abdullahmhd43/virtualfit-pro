"""
VirtualFit Pro — Flask Application Factory
============================================
Enterprise structure with:
- App factory pattern
- Blueprint registration
- Security middleware
- Rate limiting
- Centralized error handling
- Structured logging
"""

import os
import sys
import logging
# Load .env before anything else
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_app(config_obj=None) -> Flask:
    """Application factory — returns configured Flask app."""

    app = Flask(__name__, static_folder='frontend')

    # ── Config ────────────────────────────────────────────
    if config_obj is None:
        from backend.config.settings import get_config
        config_obj = get_config()
    app.config.from_object(config_obj)

    # ── Logging ───────────────────────────────────────────
    from backend.utils.logger import setup_logging
    setup_logging(app)

    # ── Database ──────────────────────────────────────────
    from backend.database.connection import init_supabase, init_mysql_pool
    init_supabase(app)
    init_mysql_pool(app)

    # ── CORS — restrict to allowed origins ───────────────
    CORS(app,
         origins=app.config.get('ALLOWED_ORIGINS', ['http://localhost:5000']),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # ── Rate Limiting ─────────────────────────────────────
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '100 per hour')],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
    )

    # ── Security Middleware ───────────────────────────────
    from backend.middleware.security import (
        apply_security_headers, log_api_request, log_api_response
    )
    app.before_request(log_api_request)
    app.after_request(apply_security_headers)
    app.after_request(log_api_response)

    # ── Error Handlers ────────────────────────────────────
    from backend.utils.errors import register_error_handlers
    register_error_handlers(app)

    # ── Blueprints ────────────────────────────────────────
    from backend.routes.auth_routes import auth_bp
    from backend.routes.ai_routes import ai_bp
    from backend.routes.core_routes import core_bp

    # Apply rate limits per blueprint
    limiter.limit(app.config.get('RATELIMIT_AUTH', '5 per minute'))(auth_bp)
    limiter.limit(app.config.get('RATELIMIT_AI', '20 per minute'))(ai_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(core_bp)

    # ── Health Check ──────────────────────────────────────
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'ok',
            'version': '2.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'services': {
                'fal': 'configured' if app.config.get('FAL_API_KEY') else 'missing',
                'gemini': 'configured' if app.config.get('GEMINI_API_KEY') else 'missing',
                'lightx': 'configured' if app.config.get('LIGHTX_API_KEY') else 'missing',
                'supabase': 'configured' if app.config.get('SUPABASE_URL') else 'missing',
                'payment': 'configured' if app.config.get('PAYHERE_SECRET') else 'unconfigured',
            }
        }), 200

    # ── Frontend — Serve Static Files ─────────────────────
    @app.route('/')
    def index():
        return send_from_directory('frontend', 'index.html')

    @app.route('/<path:filename>')
    def serve_file(filename):
        # Prevent path traversal
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Not found'}), 404
        return send_from_directory('frontend', filename)

    app.logger.info("✅ VirtualFit Pro application created")
    return app
    app = create_app()


# ── Entry Point ───────────────────────────────────────────
if __name__ == '__main__':
    flask_app = create_app()

    print("\n" + "=" * 55)
    print("  🚀 VirtualFit Pro — Enterprise Backend v2.0")
    print("=" * 55)
    print(f"  URL:       http://localhost:5000")
    print(f"  ENV:       {os.environ.get('FLASK_ENV', 'development')}")
    print(f"  FAL:       {'✅' if os.environ.get('FAL_API_KEY') else '❌ Missing'}")
    print(f"  Gemini:    {'✅' if os.environ.get('GEMINI_API_KEY') else '❌ Missing'}")
    print(f"  LightX:    {'✅' if os.environ.get('LIGHTX_API_KEY') else '❌ Missing'}")
    print(f"  Supabase:  {'✅' if os.environ.get('SUPABASE_URL') else '❌ Missing'}")
    print(f"  Payment:   {'✅' if os.environ.get('PAYHERE_SECRET') else '⚠️  Not configured'}")
    print("=" * 55 + "\n")

    # Never run debug=True in production
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    flask_app.run(debug=debug, port=5000, host='0.0.0.0')
