import pytest, re

from proj_code.validators.password_validator import password_validator

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
