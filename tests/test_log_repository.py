def test_create_log(log_repository, test_user):
    # проверка создания логов
    log_repository.create_log('/test')
    log_repository.create_log('/user', test_user.id)
    
    logs, total = log_repository.get_all_logs(per_page=10)
    assert total == 2
    
    paths = {log.path for log in logs}
    user_names = {log.user_full_name for log in logs}
    assert '/test' in paths
    assert '/user' in paths
    assert '' in user_names  # неаутентифицированный пользователь
    assert f"{test_user.last_name} {test_user.first_name} {test_user.middle_name}" in user_names

def test_get_all_logs(log_repository, test_logs):
    # проверка пагинации, сортировки и что админ видит все логи

    logs, total = log_repository.get_all_logs(per_page=3) # get_all_logs использует только админ
    assert total == 5
    assert len(logs) == 3 # 3, тк на странице указано 3 в per_page
    
    created_at = [log.created_at for log in logs]
    assert created_at == sorted(created_at, reverse=True) 

def test_get_user_logs(log_repository, test_user, test_logs):
    # видемость пользователем только своих логов
    logs, total = log_repository.get_user_logs(test_user.id, per_page=10) # пользователь использует эту функцию
    assert total == 3
    assert len(logs) == 3
    
    # проверка по имени записей, работа user_full_name
    expected_name = f"{test_user.last_name} {test_user.first_name} {test_user.middle_name}"
    assert all(log.user_full_name == expected_name for log in logs)
    
    # проверка на отсутствие пустых полей и анонима
    assert not any(log.user_full_name == 'Неаутентифицированный пользователь' for log in logs)
    assert not any(log.user_full_name is None for log in logs)

def test_get_pages_stat(log_repository, test_logs):
    # проверка верности вывода и подсчета строк страниц
    stats = log_repository.get_pages_stat()
    stats_dict = {stat.path: stat.count for stat in stats}
    
    assert stats_dict == {
        '/route1': 2,
        '/route2': 2,
        '/route3': 1
    }

def test_get_users_stat(log_repository, test_user, test_logs):
    # проверка вывода и записей пользователя и анонима
    stats = log_repository.get_users_stat()

    # анонима
    anon_stat = next((s for s in stats if s.full_name == 'Неаутентифицированный пользователь'), None)
    assert anon_stat is not None
    assert anon_stat.count == 2
    
    # пользователя
    user_stat = next((s for s in stats if s.user_id == test_user.id), None)
    assert user_stat is not None
    assert user_stat.full_name == f"{test_user.last_name} {test_user.first_name} {test_user.middle_name}"
    assert user_stat.count == 3
