from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
import mysql.connector as connector
from proj_code.validators.password_validator import password_validator
from proj_code.validators.login_validator import login_validator
from werkzeug.security import check_password_hash, generate_password_hash

from proj_code.repositories.user_repository import UserRepository
from proj_code.repositories.role_repository import RoleRepository
from proj_code.db import db

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.errorhandler(connector.errors.DatabaseError)
def handler():
    pass

@bp.route('/')
def index():
    return render_template('users/index.html', users=user_repository.all())

@bp.route('/<int:user_id>')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user.role_id)
    return render_template('users/show.html', password_error=None, login_error=None, user_data=user, user_role=getattr(user_role, 'name', ''))

@bp.route('/new', methods = ['POST', 'GET'])
@login_required
def new():
    user_data = {}
    if request.method == 'POST':
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = { field: request.form.get(field) or None for field in fields }
        
        password_error = password_validator(user_data['password']) or None
        login_error = login_validator(user_data['username']) or None
        
        
        if password_error or login_error:
            flash([password_error or '', login_error or ''], 'danger')
            return render_template('users/new.html', password_error=password_error, login_error=login_error, user_data=user_data, roles=role_repository.all())
        
        try:
            user_repository.create(**user_data)
            flash('Учетная запись успешно создана', 'success')
            return redirect(url_for('users.index'))
        except connector.errors.DatabaseError:
            flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены', 'danger')
            db.connect().rollback()
    return render_template('users/new.html', password_error=None, login_error=None, user_data=user_data, roles=role_repository.all())

@bp.route('/<int:user_id>/delete', methods = ['POST'])
@login_required
def delete(user_id):
    try:
        user_repository.delete(user_id)
        flash('Учетная запись успешно удалена', 'success')
    except Exception as e:
        flash('Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/edit', methods = ['POST', 'GET'])
@login_required
def edit(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name', 'role_id')
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
    return render_template('users/edit.html', password_error=None, login_error=None, user_data=user, roles=role_repository.all())

@bp.route('/<int:user_id>/changepassword', methods = ['POST', 'GET'])
@login_required
def changepassword(user_id):
    user = user_repository.get_by_id(user_id)
    old_password_validation = None
    passwords_not_matching = None
    password_error = None
    user_data = {}
    
    if user is None:
        flash('Пользователя нет в базе данных!', 'danger')
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        fields = ('old_password', 'new_password', 'new_password_r')
        user_data = { field: request.form.get(field) or None for field in fields }
        
        check = user_repository.validate_password(user.password, user_data['old_password'])
        
        if check is None:
            old_password_validation = "Неверный старый пароль!"
        
        if user_data['new_password'] != user_data['new_password_r']:
            passwords_not_matching = "Пароли не совпадают!"

        password_error = password_validator(user_data['new_password'])
                    
        if not password_error and not passwords_not_matching and not old_password_validation:
            try:
                user_repository.change_password(user[0], user_data["new_password"])
                flash('Пароль успешно изменен', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении пароля.', 'danger')
                db.connect().rollback()

          
    return render_template('users/changepassword.html', password_error=password_error, old_password_validation=old_password_validation, passwords_not_matching=passwords_not_matching, user_data=user_data)
