import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app
from flask import template_rendered

# фикстура для тестового клиента
@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

# фикстура для перехвата шаблонов
@pytest.fixture
def captured_templates():
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record)

# проверка шаблонов
def test_index_template(client, captured_templates):
    client.get('/')
    templates = [tpl[0].name for tpl in captured_templates]
    assert 'index.html' in templates

def test_posts_template(client, captured_templates):
    client.get('/posts')
    templates = [tpl[0].name for tpl in captured_templates]
    assert 'posts.html' in templates

def test_post_template(client, captured_templates):
    client.get('/posts/0')
    templates = [tpl[0].name for tpl in captured_templates]
    assert 'post.html' in templates

def test_about_template(client, captured_templates):
    client.get('/about')
    templates = [tpl[0].name for tpl in captured_templates]
    assert 'about.html' in templates

# проверка данных
def test_posts_context_data(client, captured_templates):
    client.get('/posts')
    context = captured_templates[0][1]
    assert 'posts' in context
    assert len(context['posts']) == 5

def test_post_context_data(client, captured_templates):
    client.get('/posts/0')
    context = captured_templates[0][1]
    assert 'post' in context
    post = context['post']
    assert all(key in post for key in ['title', 'author', 'date', 'image_id', 'text', 'comments'])

# проверка содержимого страниц
def test_post_elements_exist(client):
    response = client.get('/posts/0')
    content = response.data.decode()
    
    # проверка без привязки к данным
    assert '<h1' in content  # заголовок
    assert '<img' in content  # изображение
    assert 'class="text-justify text"' in content in content  # текст
    assert 'class="d-flex mb-4 comments"' in content.lower()  # коменты
    assert 'form' in content  # форма
    assert 'Отправить' in content  # кнопка отправки

# проверка формата даты 
def test_post_date_format(client):
    response = client.get('/posts/0')
    content = response.data.decode()
    import re
    date_format = r'\b\d{2}\.\d{2}\.\d{4}\b'
    matches = re.findall(date_format, content)
    assert len(matches) > 0
    
# проверка 404
def test_404_invalid_post(client):
    response = client.get('/posts/999')
    assert 'PAGE NOT FOUND 404' in response.data.decode()

# проверка комментариев
def test_comments_present(client):
    response = client.get('/posts/0')
    assert 'comment' in response.data.decode().lower()

def test_comment_structure(client):
    response = client.get('/posts/0')
    content = response.data.decode()
    assert 'class="d-flex mb-4 comments"' in content

def test_comment_reply(client):
    response = client.get('/posts/0')
    content = response.data.decode()
    assert '<div class="d-flex mt-4">' in content

def test_comment_avatar(client):
    response = client.get('/posts/0')
    content = response.data.decode()
    assert 'images/avatar.jpg' in content

# проверка формы комментариев
def test_comment_form_present(client):
    response = client.get('/posts/0')
    assert 'textarea' in response.data.decode()
    assert 'Отправить' in response.data.decode()

# проверка футера
def test_footer_present(client):
    response = client.get('/')
    assert 'Трубицын Вячеслав Александрович' in response.data.decode()
    assert '231-3213' in response.data.decode()