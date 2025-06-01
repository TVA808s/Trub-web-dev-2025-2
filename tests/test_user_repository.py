
def test_get_by_id_with_existing_user(user_repository, existing_user): 
    user = user_repository.get_by_id(existing_user.id)
    assert user.id == existing_user.id
    assert user.username == existing_user.username
    assert user.first_name == existing_user.first_name

def test_get_by_id_with_nonexisting_user(user_repository, nonexisting_user_id): 
    user = user_repository.get_by_id(nonexisting_user_id)
    assert user is None

def test_all_with_nonempty_db_user(user_repository, example_users): 
    users = user_repository.all()
    assert len(users) == len(example_users)
    for loaded_user, example_user in zip(users, example_users):
        assert loaded_user.id == example_user.id
        assert loaded_user.username == example_user.username

def test_get_by_username_and_password(user_repository, existing_user):
    user = user_repository.get_by_username_and_password(existing_user.username, 'password')
    assert user is not None
    assert user.id == existing_user.id

def test_get_by_username_and_password_with_wrong_password(user_repository, existing_user):
    user = user_repository.get_by_username_and_password(existing_user.username, 'wrongpassword')
    assert user is None

def test_create_user(user_repository, db_connector):
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO roles(id, name, description) VALUES (1, 'admin', 'papachka');")
        connection.commit()
    username = "newuser"
    password = "newpass"
    first_name = "New"
    middle_name = "N"
    last_name = "User"
    role_id = 1  
    
    user_repository.create(username, password, first_name, middle_name, last_name, role_id)
    
    with user_repository.db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()
        assert user is not None
        assert user.username == username
        assert user.first_name == first_name
        assert user.role_id == role_id
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE username = %s;", (username,))
        connection.commit()

def test_update_user(user_repository, existing_user):
    new_first_name = "Updated"
    new_last_name = "Name"
    
    user_repository.update(existing_user.id, new_first_name, existing_user.middle_name, new_last_name, existing_user.role_id)
    
    updated_user = user_repository.get_by_id(existing_user.id)
    assert updated_user.first_name == new_first_name
    assert updated_user.last_name == new_last_name

def test_delete_user(user_repository, existing_user):
    user_repository.delete(existing_user.id)
    deleted_user = user_repository.get_by_id(existing_user.id)
    assert deleted_user is None

def test_change_password(user_repository, existing_user):
    user_repository.change_password(existing_user.id, 'Password1337')
    assert user_repository.validate_password(existing_user.id, 'Password1337') is not None

