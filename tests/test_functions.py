import pytest, re

from proj_code.validators.password_validator import password_validator
from proj_code.validators.login_validator import login_validator
@pytest.mark.parametrize("input_password, expected_output", [
    ("1", "Пароль должен содержать как минимум 8 символов!"),
    ("fhgjdhjkghdjhfhoihhjdsjndfuwhfjbdsjhfjsbjdfjhwi9fu4uhhwu4h82h4u38h2ub2hcbiyeye447394t74bu34ght4ub37t3b8t834ut37b734n37hfuh3f3hf7473f8h3", "Пароль должен содержать не более 128 символов!"),
    ("qwertyqwerty", "Пароль должен содержать хотя бы одну заглавную букву!"),
    ("QWERTYQWERTY", "Пароль должен содержать хотя бы одну строчную букву!"),
    ("Qwertyqwerty", "Пароль должен содержать хотя бы одну цифру!"),
    ("Qwertyqwerty 18", "Пароль не должен содержать пробелов!"),
    ("Qwerty18", None)
])
def test_password_validation(input_password, expected_output):
    assert password_validator(input_password) == expected_output


@pytest.mark.parametrize("input_login, expected_output", [
    ("user", "Логин должен содержать как минимум 5 символов!"),
    ("пользователь", "Используются запрещенные символы! Вводите только латинские буквы, цифры"),
    ("USER/222", "Используются запрещенные символы! Вводите только латинские буквы, цифры"),
    ("user123", None)
])
def test_login_validation(input_login, expected_output):
    assert login_validator(input_login) == expected_output
