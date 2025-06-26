import pytest
import mysql.connector
from mysql.connector import errorcode
from pathlib import Path
import os
import sys
from collections import namedtuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from proj_code.app import create_app
from proj_code.db import DBConnector
from proj_code.repositories.meeting_repository import MeetingRepository
from proj_code.repositories.user_repository import UserRepository

TEST_DB_CONFIG = {
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': 'pythonanywhere',
    'MYSQL_HOST': 'localhost',
    'MYSQL_DATABASE': 'test_db',
    'TESTING': True
}

def read_schema_file(schema_path):
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(schema_path, 'r', encoding='cp1251') as f:
            return f.read()

@pytest.fixture(scope='session')
def app():
    app = create_app(TEST_DB_CONFIG)
    app.config.update(TEST_DB_CONFIG)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def db_connection():
    """Фикстура подключения к тестовой БД"""
    admin_conn = mysql.connector.connect(
        user=TEST_DB_CONFIG['MYSQL_USER'],
        password=TEST_DB_CONFIG['MYSQL_PASSWORD'],
        host=TEST_DB_CONFIG['MYSQL_HOST']
    )
    
    with admin_conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_CONFIG['MYSQL_DATABASE']}")
        admin_conn.commit()
    
    conn = mysql.connector.connect(
        user=TEST_DB_CONFIG['MYSQL_USER'],
        password=TEST_DB_CONFIG['MYSQL_PASSWORD'],
        host=TEST_DB_CONFIG['MYSQL_HOST'],
        database=TEST_DB_CONFIG['MYSQL_DATABASE']
    )
    
    schema_path = Path(__file__).parent.parent / 'proj_code' / 'schema.sql'
    schema_sql = read_schema_file(schema_path)
    
    with conn.cursor() as cursor:
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
    
    yield conn
    conn.close()
