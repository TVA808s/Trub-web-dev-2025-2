from functools import reduce
from collections import namedtuple
import logging
import pytest
import mysql.connector
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from proj_code.app import create_app
from proj_code.db import DBConnector
from proj_code.repositories.role_repository import RoleRepository
from proj_code.repositories.user_repository import UserRepository
from proj_code.repositories.log_repository import LogRepository
from datetime import timedelta, datetime 

TEST_DB_CONFIG = {
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': 'pythonanywhere',
    'MYSQL_HOST': 'localhost',
    'MYSQL_DATABASE': 'trubitsyn_lab4_test',
}

def get_connection(app):
    return mysql.connector.connect(
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        host=app.config['MYSQL_HOST']
    )

def setup_db(app):
    logging.getLogger().info("Create db...")
    test_db_name = app.config['MYSQL_DATABASE']
    create_db_query = (f'DROP DATABASE IF EXISTS {test_db_name}; '
                       f'CREATE DATABASE {test_db_name}; '
                       f'USE {test_db_name};')

    with app.open_resource('schema.sql') as f:
        schema_query = f.read().decode('utf8')

    connection = get_connection(app)
    query = '\n'.join([create_db_query, schema_query])
    with connection.cursor(named_tuple=True) as cursor:
        for _ in cursor.execute(query, multi=True):
                pass
    connection.commit()
    connection.close()


def teardown_db(app):
    logging.getLogger().info("Drop db...")
    test_db_name = app.config['MYSQL_DATABASE']
    connection = get_connection(app)
    with connection.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS {test_db_name};')
    connection.close()

    
@pytest.fixture(scope='session')
def app():
    return create_app(TEST_DB_CONFIG)

@pytest.fixture(scope='session')
def db_connector(app):
    setup_db(app)
    with app.app_context():
        connector = DBConnector(app)
        yield connector
        connector.disconnect()
    teardown_db(app)

@pytest.fixture
def role_repository(db_connector):
    return RoleRepository(db_connector)

@pytest.fixture(autouse=True)
def auto_cleanup(db_connector):
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM roles;")
        cursor.execute("DELETE FROM visit_logs;")
        connection.commit()
    yield


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_repository(db_connector):
    return UserRepository(db_connector)


@pytest.fixture
def log_repository(db_connector):
    return LogRepository(db_connector)


from werkzeug.security import generate_password_hash

# Добавляем фикстуру для автоматической очистки
@pytest.fixture(autouse=True)
def auto_cleanup(db_connector):
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM visit_logs;")
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM roles;")
        connection.commit()
    yield

# Фикстура для тестовой роли
@pytest.fixture
def test_role(db_connector):
    role_data = (3, 'Тестовая роль', 'Описание тестовой роли')
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)",
            role_data
        )
        connection.commit()
    
    Role = namedtuple('Role', ['id', 'name', 'description'])
    return Role(*role_data)

# Фикстура для тестового пользователя
@pytest.fixture
def test_user(db_connector, test_role):
    user_data = (
        100, 
        'test_user', 
        generate_password_hash('test_password'),
        'Иван', 
        'Иванович', 
        'Иванов',
        test_role.id
    )
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (id, username, password, first_name, last_name, middle_name, role_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            user_data
        )
        connection.commit()
    
    User = namedtuple('User', ['id', 'username', 'password', 'first_name', 'last_name', 'middle_name', 'role_id'])
    return User(*user_data)

@pytest.fixture
def test_logs(db_connector, test_user):
    base_time = datetime.now()
    logs_data = [
        ('/route1', None, base_time - timedelta(minutes=10)),
        ('/route2', None, base_time - timedelta(minutes=5)),
        ('/route1', test_user.id, base_time - timedelta(minutes=3)),
        ('/route2', test_user.id, base_time - timedelta(minutes=2)),
        ('/route3', test_user.id, base_time - timedelta(minutes=1)),
    ]
    
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        query = "INSERT INTO visit_logs (path, user_id, created_at) VALUES (%s, %s, %s)"
        cursor.executemany(query, logs_data)
        connection.commit()
    return len(logs_data)