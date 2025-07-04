from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import mysql.connector as connector
from functools import wraps
from proj_code.repositories.user_repository import UserRepository
from proj_code.repositories.meeting_repository import MeetingRepository
from proj_code.db import db
from math import ceil
from bleach.sanitizer import Cleaner
import os
from werkzeug.utils import secure_filename

cleaner = Cleaner()
meeting_repository = MeetingRepository(db)
user_repository = UserRepository(db)

bp = Blueprint('meetings', __name__, url_prefix='/meetings')

login_manager = LoginManager()
login_manager.login_view = 'meetings.login'
login_manager.login_message = 'Авторизуйтесь для доступа к ресурсу.'
login_manager.login_message_category = 'warning'


def check_rights(req_role):
    def decorator(func):
        @wraps(func) 
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для выполнения данного действия необходимо пройти процедуру аутентификации', 'danger')
                return redirect(url_for('meetings.login'))
            
            if req_role == 'Администратор' and current_user.role_name != 'Администратор':
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('meetings.index'))

            if req_role == 'Модератор' and current_user.role_name not in ['Модератор', 'Администратор']:                
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('meetings.index'))
            
            return func(*args, **kwargs)
        return decorated_function
    return decorator

class User(UserMixin):
    def __init__(self, user_id, login, role_name, full_name):
        self.id = user_id
        self.login = login
        self.role_name = role_name
        self.full_name = full_name

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user.id, user.login, user.role_name, user.full_name)
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('meetings.index'))
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        user = user_repository.get_by_login_and_password(login, password)
        if user is not None:
            flash('Авторизация прошла успешно', 'success')
            login_user(User(user.id, user.login, user.role_name, user.full_name), remember=remember_me)
            next_url = request.args.get('next', url_for('meetings.index'))
            return redirect(next_url)
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('meetings/login.html', title='Войти')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('meetings.index'))

@bp.errorhandler(connector.errors.DatabaseError)
def handler():
    pass

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    meetings, total = meeting_repository.get_all_meetings(page, per_page)
    total_pages = ceil(total / per_page) if total > 0 else 1
    if page < 1 or (total_pages > 0 and page > total_pages):
        flash('Запрошенная страница не существует', 'warning')
        return redirect(url_for('meetings.index'))
    
    role = False
    if current_user.is_authenticated:
        role = current_user.role_name

    return render_template(
        'meetings/index.html', 
        role=role, 
        meetings=meetings, 
        current_page=page, 
        total_pages=total_pages
    )


@bp.route('/<int:meeting_id>/registration', methods=['POST'])
@login_required
def registration(meeting_id):
    action = request.form.get('action')
    registration_id = request.form.get('registration_id')

    if current_user.role_name not in ['Модератор', 'Администратор']:
        flash('У вас недостаточно прав', 'danger')
        return redirect(url_for('meetings.getMeeting', meeting_id=meeting_id))
    
    if action == 'accept':
        meeting_repository.set_status(registration_id, 'accepted')
        flash('Заявка принята', 'success')
        meeting = meeting_repository.get_meeting_by_id(meeting_id)
        if meeting.volunteers_count >= meeting.volunteers_amount:
            meeting_repository.reject_all_pending(meeting_id)
            flash('Лимит волонтеров достигнут. Оставшиеся заявки отклонены.', 'info')
            
    elif action == 'reject':
        meeting_repository.set_status(registration_id, 'rejected')
        flash('Заявка отклонена', 'info')

    return redirect(url_for('meetings.getMeeting', meeting_id=meeting_id))


@bp.route('/<int:meeting_id>')
def getMeeting(meeting_id):
    meeting = meeting_repository.get_meeting_by_id(meeting_id)
    if meeting is None:
        flash('Мероприятие не найдено', 'danger')
        return redirect(url_for('meetings.index'))

    role = False
    already_registr = False
    if current_user.is_authenticated:
        role = current_user.role_name
        already_registr = user_repository.get_reg_user_or_not(meeting_id, current_user.id)

    if role in ['Администратор', 'Модератор']:
        accepted_volunteers = meeting_repository.get_accepted_volunteers(meeting_id)
        pending_volunteers = meeting_repository.get_pending_volunteers(meeting_id)
    else:
        accepted_volunteers = False
        pending_volunteers = False

    return render_template(
        'meetings/getMeeting.html',
        meeting=meeting,
        accepted_volunteers=accepted_volunteers,
        pending_volunteers=pending_volunteers,
        role=role,
        already_registr=already_registr
    )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@bp.route('/createMeeting', methods = ['POST', 'GET'])
@login_required
@check_rights('Администратор')
def createMeeting():
    meeting = {}
    errors = {}
    # полный путь для сохранения фото
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static/uploads')

    if request.method == 'POST':
        fields = ('title', 'description', 'date', 'place', 'volunteers_amount')
        for field in fields:
            value = request.form.get(field)        
            if value == '' or value is None:
                errors[field] = 'Введите значение'
                meeting[field] = '' 
            else:
                meeting[field] = cleaner.clean(value)

        meeting['organizer'] = current_user.id

        if 'image' not in request.files:
            errors['image'] = 'Файл изображения не найден'
        else:
            image = request.files['image']
            
            if image.filename == '':
                errors['image'] = 'Выберите изображение'
            elif image and allowed_file(image.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(image.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(save_path)
                
                # относительный путь для бд
                meeting['image'] = os.path.join('uploads', filename)
            else:
                errors['image'] = 'Допустимые форматы: .png, .jpg, .jpeg, .gif'
        
        if errors:
            flash('Исправьте ошибки в форме', 'danger')
        else:
            try:
                meeting_repository.create(**meeting)
                flash('Мероприятие успешно создано', 'success')
                return redirect(url_for('meetings.index'))
            except connector.errors.DatabaseError:
                flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных', 'danger')
                connection = meeting_repository.db_connector.connect()
                connection.rollback()

    return render_template('meetings/createMeeting.html', meeting=meeting, errors=errors)


@bp.route('/<int:meeting_id>/editMeeting', methods = ['POST', 'GET'])
@login_required
@check_rights('Модератор')
def editMeeting(meeting_id):
    meeting = {}
    errors = {}

    if request.method == 'POST':
        fields = ('title', 'description', 'date', 'place', 'volunteers_amount')
        for field in fields:
            value = request.form.get(field)        
            if value == '' or value is None:
                errors[field] = 'Введите значение'
                meeting[field] = '' 
            else:
                meeting[field] = cleaner.clean(value)

        if errors:
            flash('Исправьте ошибки в форме', 'danger')
        else:
            try:
                meeting_repository.edit(meeting_id,**meeting)
                flash('Мероприятие успешно отредактированно', 'success')
                return redirect(url_for('meetings.index'))
            except connector.errors.DatabaseError:
                flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных', 'danger')
                connection = meeting_repository.db_connector.connect()
                connection.rollback()
    if request.method == 'GET':
        meeting = meeting_repository.get_meeting_by_id(meeting_id)

    return render_template('meetings/editMeeting.html', meeting=meeting, errors=errors)


@bp.route('/<int:meeting_id>/delete', methods = ['POST'])
@login_required
@check_rights('Администратор')
def delete(meeting_id):
    try:
        meeting_repository.delete(meeting_id)
        flash('Запись успешно удалена', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('meetings.index'))


@bp.route('/<int:meeting_id>/registrate', methods=['POST'])
@login_required
def registrate(meeting_id):
    try:
        contacts = request.form.get('contacts')
        if contacts:
            meeting_repository.registrate(meeting_id, current_user.id, contacts)
            flash('Запись успешно создана', 'success')
        else:
            flash('Укажите ваши данные', 'danger')
    except Exception as e:
        flash(f'Ошибка при создании: {e}', 'danger')
    return redirect(url_for('meetings.getMeeting', meeting_id=meeting_id)) 

