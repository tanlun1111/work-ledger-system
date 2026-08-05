from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def _ensure_mysql_database(db_uri):
    import pymysql
    import re

    match = re.match(r"mysql\+pymysql://(.+):(.+)@(.+):(\d+)/([^?]+)", db_uri)
    if not match:
        return

    user, password, host, port, db_name = match.groups()
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()


def create_app(config_name="development"):
    import os
    from config import config_map

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    _ensure_mysql_database(app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_current_user():
        from app.models.user import User
        if hasattr(g, 'current_user'):
            return {"current_user": g.current_user}
        uid = session.get("user_id")
        if uid:
            user = User.query.get(uid)
            if user and user.is_active:
                g.current_user = user
                return {"current_user": user}
        return {}

    from app.errors import register_error_handlers
    register_error_handlers(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_TMP_FOLDER"], exist_ok=True)

    with app.app_context():
        from app.models.enum_config import EnumConfig
        from app.models.user import User
        from app.models.police_station import PoliceStation
        from app.models.investigation_flow import InvestigationFlow
        from app.models.investigation_flow_attachment import InvestigationFlowAttachment
        db.create_all()
        EnumConfig.init_defaults()
        User.init_default_admin()
        PoliceStation.init_defaults()

    return app
