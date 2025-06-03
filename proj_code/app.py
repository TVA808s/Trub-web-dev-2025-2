# app.py
import os
from flask import Flask, session, request
from flask_login import current_user
from proj_code.db import db
from proj_code.repositories.log_repository import LogRepository

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    
    # Загрузка конфигурации
    app.config.from_pyfile('config.py', silent=False)
    
    if test_config:
        app.config.update(test_config)

    # Инициализация базы данных
    db.init_app(app)
    
    # Регистрация CLI-команд
    from proj_code.cli import init_db_command  
    app.cli.add_command(init_db_command)
    
    # Регистрация блюпринтов
    from proj_code.users import bp as users_bp, index, login_manager
    login_manager.init_app(app)
    app.register_blueprint(users_bp)
    app.add_url_rule('/', 'index', index)
    from proj_code.logs import bp as logs_bp
    app.register_blueprint(logs_bp)

    @app.before_request
    def log_visit():
        if request.path.startswith('/static'):
            return
        user_id = current_user.id if current_user.is_authenticated else None
        logs_repo = LogRepository(db)
        logs_repo.create_log(request.path, user_id)

    return app

app = create_app()
