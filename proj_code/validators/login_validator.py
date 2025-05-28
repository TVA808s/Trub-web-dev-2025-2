import re

def login_validator(login):
    if login is None or len(login) < 5:
        return "Пароль должен содержать как минимум 5 символов!"
    allowed_characters = r'^[A-Za-z0-9]+$'
    if not re.match(allowed_characters, login):
        return r"Используются запрещенные символы! Вводите только латинские буквы, цифры"
    return None