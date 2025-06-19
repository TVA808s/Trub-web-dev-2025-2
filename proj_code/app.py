from flask import Flask
from proj_code.db import db
import markdown

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    
    # Загрузка конфигурации
    app.config.from_pyfile('config.py', silent=False)
    
    if test_config:
        app.config.update(test_config)

    # Инициализация базы данных
    db.init_app(app)
    
    # Регистрация блюпринтов
    from proj_code.meetings import bp as meetings_bp, index, login_manager
    login_manager.init_app(app)
    app.register_blueprint(meetings_bp)
    app.add_url_rule('/', 'index', index)

    # Обработка markdown в html
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        return markdown.markdown(text, extensions=[
            'fenced_code',  # Блоки кода
            'tables',       # Таблицы
            'nl2br',        # Автоматический перенос строк
            'sane_lists'    # Улучшенные списки
        ])
    
    return app

app = create_app()
