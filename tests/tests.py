import io
from proj_code.config import PASS

def decode_response(response):
    try:
        return response.data.decode('utf-8')
    except UnicodeDecodeError:
        return response.data.decode('cp1251')

def login(client, role):
    with client:
        response = client.post('meetings/login', data={
            'login': f'{role}',
            'password': f'{PASS}'
        }, follow_redirects=True)
        assert response.status_code == 200

#db_connection чтобы данные пересоздались и тестирование работало
def test_anonim_main(client, db_connection):
    with db_connection:
        assert 1
    response = client.get('/')
    content = decode_response(response)
    assert 'Обучение пожилых людей' in content
    assert 'Добавить мероприятие' not in content
    assert 'Удалить' not in content
    assert 'Редактирование' not in content

def test_user_main(client):
    login(client, 'user')

    response = client.get('/')
    content = decode_response(response)
    assert 'Обучение пожилых людей' in content
    assert 'Добавить мероприятие' not in content
    assert 'Удалить' not in content
    assert 'Редактирование' not in content
    
def test_moder_main(client):
    login(client, 'moder')

    response = client.get('/')
    content = decode_response(response)
    assert 'Обучение пожилых людей' in content
    assert 'Добавить мероприятие' not in content
    assert 'Удалить' not in content
    assert 'Редактирование' in content

def test_admin_main(client):
    login(client, 'admin')

    response = client.get('/')
    content = decode_response(response)
    assert 'Обучение пожилых людей' in content
    assert 'Добавить мероприятие' in content
    assert 'Удалить' in content
    assert 'Редактирование' in content


def test_anonim_previleges(client):  
    response = client.get('meetings/createMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'Авторизуйтесь для доступа к ресурсу.' in content

    response = client.get('meetings/1/editMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'Авторизуйтесь для доступа к ресурсу.' in content

    response = client.post('meetings/1/delete', follow_redirects=True)
    content = decode_response(response)
    assert 'Авторизуйтесь для доступа к ресурсу.' in content


def test_user_previleges(client):
    login(client, 'user')

    response = client.get('meetings/createMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'У вас недостаточно прав' in content

    response = client.get('meetings/1/editMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'У вас недостаточно прав' in content

    response = client.post('meetings/1/delete', follow_redirects=True)
    content = decode_response(response)
    assert 'У вас недостаточно прав' in content


def test_moder_previleges(client):
    login(client, 'moder')

    response = client.get('meetings/createMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'У вас недостаточно прав' in content

    response = client.get('meetings/1/editMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'Редактирование мероприятия' in content

    response = client.post('meetings/2/delete', follow_redirects=True)
    content = decode_response(response)
    assert 'У вас недостаточно прав' in content


def test_admin_previleges_and_delete_meeting(client):
    login(client, 'admin')

    response = client.get('meetings/createMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'Добавление мероприятия' in content

    response = client.get('meetings/1/editMeeting', follow_redirects=True)
    content = decode_response(response)
    assert 'Редактирование мероприятия' in content

    response = client.get('/')
    assert 'Благотворительный забег' in decode_response(response)
    
    response = client.post('meetings/3/delete', follow_redirects=True)

    response = client.get('/')
    assert 'Благотворительный забег' not in decode_response(response)


def test_anonim_meeting_page(client):
    response = client.get('meetings/1')
    content = decode_response(response)
    assert 'Уборка парка' in content
    assert 'Вы уже зарегистрированны' not in content
    assert 'Зарегистрироваться' not in content


def test_user_meeting_page(client):
    login(client, 'user')

    response = client.get('meetings/1')
    content = decode_response(response)
    assert 'Уборка парка' in content
    assert 'Вы уже зарегистрированны' in content


def test_create_meeting(client):
    login(client, 'admin')

    test_image = (io.BytesIO(b'test image content'), 'test.png')
    response = client.post('meetings/createMeeting', data={
        'image': test_image,
        'title' : 'test meeting',
        'description' : 'this is a test',
        'date' : '2026-01-01',
        'place' : 'moscow',
        'volunteers_amount' : '2'
    }, follow_redirects=True, content_type='multipart/form-data')

    response = client.get('/')
    assert 'test meeting' in decode_response(response)



def test_edit_meeting(client):
    login(client, 'admin')
    test_image = (io.BytesIO(b'test image content'), 'test.png')
    response = client.post('meetings/2/editMeeting', data={
        'image': test_image,
        'title' : 'edit admin',
        'description' : 'this is a test',
        'date' : '2026-01-01',
        'place' : 'moscow',
        'volunteers_amount' : '2'
    }, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/')
    assert 'edit admin' in decode_response(response)


def test_accept_decline_rejectAll(client):
    login(client, 'moder')
    response = client.get('meetings/4')
    assert 'rejected' not in decode_response(response)


    login(client, 'admin')
    response = client.get('meetings/4')
    assert 'Идёт набор волонтёров' in decode_response(response)

    response = client.post('meetings/4/registration', data={
        'action': 'accept',
        'registration_id':'11',
        }, follow_redirects=True)

    response = client.get('meetings/4')
    assert 'Идёт набор волонтёров' not in decode_response(response)
    assert 'Регистрация закрыта' in decode_response(response)


    login(client, 'moder')
    response = client.get('meetings/4')
    assert 'rejected' in decode_response(response)
    

def test_registration(client):
    login(client, 'user')
    response = client.post('meetings/5/registrate', data={
        'contacts': '12345'
    }, follow_redirects=True)
    assert 'Запись успешно создана' in decode_response(response)

    login(client, 'moder')
    response = client.post('meetings/5/registrate', data={}, follow_redirects=True)
    assert 'Укажите ваши данные' in decode_response(response)
        