import pytest, re

def test_visits_counter(client):
    response = client.get("/visitscounter")
    assert response.status_code == 200
    page_content = response.get_data(as_text=True)
    assert "1" in page_content
    client.get("/visitscounter")
    client.get("/visitscounter")
    response = client.get("/visitscounter")
    page_content = response.get_data(as_text=True)
    assert "4" in page_content
    
def test_visits_counter_for_user(client):
    client.get("/visitscounter")
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    response = client.get("/visitscounter")
    assert response.status_code == 200
    page_content = response.get_data(as_text=True)
    assert "1" in page_content
    assert "2" in page_content
    client.get("/visitscounter")
    client.get("/visitscounter")
    response = client.get("/visitscounter")
    page_content = response.get_data(as_text=True)
    assert "4" in page_content
    assert "5" in page_content
    
def test_navbar_logged_in_logged_out(client):
    response = client.get('/')
    page_content = response.get_data(as_text=True)
    assert "Вход" in page_content
    assert "Счётчик посещений" in page_content
    assert "Выход" not in page_content
    assert "Секретная страница" not in page_content
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert "Вход" not in page_content
    assert "Счётчик посещений" in page_content
    assert "Выход" in page_content
    assert "Секретная страница" in page_content


    
def test_login_redirect_after_authentication(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert 'Вы успешно аутентифицированы!' in page_content
    assert 'Добро пожаловать, user!' in page_content
    assert response.request.path == '/'
    # print(page_content)
    assert '/logout' in page_content
    
def test_login_with_wrong_data(client):
    response = client.post('/login', data={
        'username': 'user2',
        'password': 'qwert'
    }, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert 'Введены неверные данные!' in page_content
    
def test_login_with_uncompleted_data(client):
    response = client.post('/login', data={
        'username': 'user2',
    }, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert 'Необходимо заполнить все поля!' in page_content
    
def test_login_with_no_data(client):
    response = client.post('/login', data={}, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert 'Необходимо заполнить все поля!' in page_content
    
def test_secret_page_is_hidden(client):
    response = client.get('/')
    page_content = response.get_data(as_text=True)
    assert '/secretpage' not in page_content
    
def test_secret_page_is_not_hidden(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert '/secretpage' in page_content
    
def test_unauthorized_user_secret_redirect(client):
    response = client.get('/secretpage', follow_redirects=True)
    page_content = response.get_data(as_text=True)
    assert response.request.path == '/login'
    assert 'Войдите в аккаунт для доступа к материалам сайта)' in page_content
    
def test_remember_me_token_setted(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'on'
    })
    
    set_cookie =  response.headers.get('Set-Cookie')
    
    assert 'remember_token=' in set_cookie
    assert 'Expires' in set_cookie
    
def test_remember_me_token_not_setted(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'off'
    })
    
    assert 'remember_token=' not in response.headers.get('Set-Cookie')
    
def test_unauthorized_user_secret_redirect_after_login(client):
    response = client.get('/secretpage', follow_redirects=True)
    assert 'next=/secretpage' in response.request.url


    response2 = client.post(response.request.url, data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    assert response2.request.path == '/secretpage'
    page_content = response2.get_data(as_text=True)
    assert 'ITSASECRET' in page_content