import re

def password_validator(password):
    if password is None or len(password) < 8:
        return "Пароль должен содержать как минимум 8 символов!"
    if len(password) > 128:
        return "Пароль должен содержать не более 128 символов!"
    if not re.search(r'[А-ЯA-Z]',password):
        return "Пароль должен содержать хотя бы одну заглавную букву!"
    if not re.search(r'[а-яa-z]',password):
        return "Пароль должен содержать хотя бы одну строчную букву!"
    if not re.search(r'[0-9]', password):
        return "Пароль должен содержать хотя бы одну цифру!"
    if " " in password:
        return "Пароль не должен содержать пробелов!"
    
    allowed_characters = r'^[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+\(\)\[\]\{\}><\/\\|\"\'.,:;]+$'
    
    if not re.match(allowed_characters, password):
        return r"Используются запрещенные символы! Вводите только латинские или кириллические буквы, цифры 0-9, а также любые из спец. символов: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" ' . , : ;"

    return None
