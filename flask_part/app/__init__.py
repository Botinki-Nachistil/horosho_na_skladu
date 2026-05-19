from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

from app.config import get_settings
from app.exceptions import APIError
from app.extensions import db, scheduler


def create_app() -> Flask:
    app = Flask(__name__)
    settings = get_settings()

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.postgres_dsn
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    app.config["DEBUG"] = settings.debug
    app.config["SCHEDULER_API_ENABLED"] = False

    db.init_app(app)
    scheduler.init_app(app)
    if settings.enable_scheduler:
        scheduler.start()

    CORS(app, origins=settings.cors_origins)

    _register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/healthz")
    def healthcheck():
        return jsonify({"status": "ok"})

    return app


def _register_blueprints(app: Flask) -> None:
    from app.incidents.routes import incidents_bp
    from app.integrations.routes import integrations_bp
    from app.kpi.routes import kpi_bp

    app.register_blueprint(incidents_bp, url_prefix="/api/v1/incidents")
    app.register_blueprint(kpi_bp, url_prefix="/api/v1/kpi")
    app.register_blueprint(integrations_bp, url_prefix="/api/v1/integrations")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        return jsonify({"error": {"code": error.code, "message": error.message}}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": {"code": "not_found", "message": "Resource not found"}}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": {"code": "method_not_allowed", "message": "Method not allowed"}}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception(error)
        return jsonify({"error": {"code": "internal_error", "message": "An unexpected error occurred"}}), 500
