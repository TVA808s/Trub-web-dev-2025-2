from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import mysql.connector as connector
from proj_code.validators.password_validator import password_validator
from proj_code.validators.login_validator import login_validator
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from proj_code.repositories.user_repository import UserRepository
from proj_code.repositories.role_repository import RoleRepository
from proj_code.db import db
from math import ceil

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = 'Авторизуйтесь для доступа к ресурсу.'
login_manager.login_message_category = 'warning'


def check_rights(req_role):
    def decorator(func):
        @wraps(func) 
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Войдите в аккаутн.', 'danger')
                return redirect(url_for('users.login'))
            
            user = user_repository.get_by_id(current_user.id)
            role = role_repository.get_by_id(user.role)
            
            if req_role == 'Администратор' and role.name != 'Администратор':
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('users.index'))

            if req_role == 'Модератор' and role.name not in ['Модератор', 'Администратор']:                
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('users.index'))
            
            return func(*args, **kwargs)
        return decorated_function
    return decorator


class User(UserMixin):
    def __init__(self, user_id, login, role):
        self.id = user_id
        self.login = login
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user.id, user.login, user.role)
    return None


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        user = user_repository.get_by_login_and_password(login, password)
        
        if user is not None:
            flash('Авторизация прошла успешно', 'success')
            login_user(User(user.id, user.login, user.role), remember=remember_me)
            next_url = request.args.get('next', url_for('users.index'))
            return redirect(next_url)
        
        flash('Пользователь не найден, проверьте корректность введенных данных', 'danger')

    return render_template('users/login.html', title='Войти')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.index'))


@bp.errorhandler(connector.errors.DatabaseError)
def handler():
    pass

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    meetings, total = user_repository.get_all_meetings(page, per_page)
    total_pages = ceil(total / per_page) if total > 0 else 1
    if page < 1 or (total_pages > 0 and page > total_pages):
        flash('Запрошенная страница не существует', 'warning')
        return redirect(url_for('users.index'))
    
    role = ''
    if current_user.is_authenticated:
        sender = user_repository.get_by_id(current_user.id)
        if sender:
            sender_role = role_repository.get_by_id(sender.role)
            role = sender_role.name  
    return render_template(
        'users/index.html', 
        role=role, 
        meetings=meetings, 
        current_page=page, 
        total_pages=total_pages
    )

@bp.route('/<int:meeting_id>')
@login_required
def getMeeting(meeting_id):
    action = request.args.get('action')
    registration_id = request.args.get('registration_id')
    if action and registration_id:
        if action == 'accept':
            user_repository.set_status(registration_id, 'accepted')
            flash('Заявка принята', 'success')
        elif action == 'reject':
            user_repository.set_status(registration_id, 'rejected')
            flash('Заявка отклонена', 'warning')

    meeting = user_repository.get_meeting_by_id(meeting_id)
    if meeting is None:
        flash('Мероприятие не найдено', 'danger')
        return redirect(url_for('users.index'))
    
    accepted_volunteers = user_repository.get_accepted_volunteers(meeting_id)
    pending_volunteers = user_repository.get_pending_volunteers(meeting_id)

    return render_template(
        'users/getMeeting.html',
        meeting=meeting,
        accepted_volunteers=accepted_volunteers,
        pending_volunteers=pending_volunteers
    )


@bp.route('/createUser', methods = ['POST', 'GET'])
@login_required
@check_rights('Администратор')
def createUser():
    user_data = {}
    if request.method == 'POST':
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = { field: request.form.get(field) or None for field in fields }
        
        password_error = password_validator(user_data['password']) or None
        login_error = login_validator(user_data['username']) or None
        
        
        if password_error or login_error:
            flash([password_error or '', login_error or ''], 'danger')
            return render_template('users/createUser.html', password_error=password_error, login_error=login_error, user_data=user_data, roles=role_repository.all())
        
        try:
            user_repository.create(**user_data)
            flash('Учетная запись успешно создана', 'success')
            return redirect(url_for('users.index'))
        except connector.errors.DatabaseError:
            flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены', 'danger')
            db.connect().rollback()
    return render_template('users/createUser.html', password_error=None, login_error=None, user_data=user_data, roles=role_repository.all())

@bp.route('/<int:meeting_id>/delete', methods = ['POST'])
@login_required
@check_rights('Администратор')
def delete(meeting_id):
    try:
        user_repository.delete(meeting_id)
        flash('Запись успешно удалена', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/updateName', methods = ['POST', 'GET'])
@login_required
def updateName(user_id):
    sender = user_repository.get_by_id(current_user.id)
    sender_role = role_repository.get_by_id(sender.role_id)
    if current_user.id != user_id and sender_role.name != 'Администратор':
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('users.index'))
    
    roles = None
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))
    if request.method == 'POST':
        if sender_role.name == 'Администратор':
            fields = ('first_name', 'middle_name', 'last_name', 'role_id')
            roles = role_repository.all()
        else:
            fields = ('first_name', 'middle_name', 'last_name')
        user_data = { field: request.form.get(field) or None for field in fields }
        if user_data['first_name'] == None or user_data['middle_name'] == None:
            flash('Имя и Отчество должны быть введены','danger')
            user = user_data
        else:
            try:
                user_repository.update(user_id, **user_data)
                flash('Учетная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении записи.', 'danger')
                db.connect().rollback()
                user = user_data
    return render_template('users/updateName.html', password_error=None, login_error=None, user_data=user, roles=roles)

@bp.route('/<int:user_id>/updatePassword', methods = ['POST', 'GET'])
@login_required
def updatePassword(user_id):
    sender = user_repository.get_by_id(current_user.id)
    sender_role = role_repository.get_by_id(sender.role_id)
    if current_user.id != user_id and sender_role.name != 'Администратор':
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('users.index'))
    
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))
    
    old_password_validation = None
    passwords_not_matching = None
    password_error = None
    user_data = {}
    if request.method == 'POST':
        fields = ('old_password', 'new_password', 'new_password_r')
        user_data = { field: request.form.get(field) or None for field in fields }
        
        check = user_repository.validate_password(user_id, user_data['old_password'])
        
        if check is None:
            old_password_validation = "Неверный старый пароль!"
        
        if user_data['new_password'] != user_data['new_password_r']:
            passwords_not_matching = "Пароли не совпадают!"

        password_error = password_validator(user_data['new_password'])

        if not password_error and not passwords_not_matching and not old_password_validation:
            try:
                user_repository.change_password(user_id, user_data["new_password"])
                flash('Пароль успешно изменен', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении пароля.', 'danger')
                db.connect().rollback()


    return render_template('users/updatePassword.html', password_error=password_error, old_password_validation=old_password_validation, passwords_not_matching=passwords_not_matching, user_data=user_data)
