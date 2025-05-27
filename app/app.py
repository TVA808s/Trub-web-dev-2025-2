# app.py
import os
from flask import Flask, session
from app.db import db 

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    
    # Загрузка конфигурации
    app.config.from_pyfile('config.py', silent=False)
    
    if test_config:
        app.config.update(test_config)

    # Инициализация базы данных
    db.init_app(app)
    
    # Регистрация CLI-команд
    from cli import init_db_command  
    app.cli.add_command(init_db_command)
    
    # Регистрация блюпринтов
    from auth import bp as auth_bp, login_manager
    app.register_blueprint(auth_bp)
    login_manager.init_app(app)
    
    from users import bp as users_bp, index
    app.register_blueprint(users_bp)
    app.add_url_rule('/', 'index', index)
    
    return app

app = create_app()
