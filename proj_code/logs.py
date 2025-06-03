from flask import Blueprint, flash, redirect, render_template, request, url_for, Response
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import mysql.connector as connector
from proj_code.validators.password_validator import password_validator
from proj_code.validators.login_validator import login_validator
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from proj_code.repositories.user_repository import UserRepository
from proj_code.repositories.role_repository import RoleRepository
from proj_code.db import db
from proj_code.repositories.log_repository import LogRepository

bp = Blueprint('logs', __name__, url_prefix='/logs')
log_repository = LogRepository(db)
user_repository = UserRepository(db)
role_repository = RoleRepository(db)

@bp.route('/visit_log')
def visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user = user_repository.get_by_id(current_user.id)
    role = role_repository.get_by_id(user.role_id)
    if role.name == 'Администратор':
        logs, total = log_repository.get_all_logs(page, per_page)
    else:
        logs, total = log_repository.get_user_logs(current_user.id, page, per_page)
    return render_template(
        'logs/visit_log.html',
        logs=logs,
        page=page,
        per_page=per_page,
        total=total
    )

@bp.route('/pages_stat')
@login_required
def pages_stat():
    stats = log_repository.get_pages_stat()

    if request.args.get('export') == '1':
        csv_data = "№,Страница,Количество посещений\n"
        for i, row in enumerate(stats, 1):
            csv_data += f"{i},{row.path},{row.count}\n"  
        return Response(
            csv_data,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-disposition": "attachment; filename=pages_stat.csv"}
        )
    return render_template('logs/pagesStat.html', logs=stats)

@bp.route('/users_stat')
@login_required
def users_stat():
    stats = log_repository.get_users_stat()

    if request.args.get('export') == '1':
        csv_data = "№,Пользователь,Количество посещений\n"
        for i, row in enumerate(stats, 1):
            csv_data += f"{i},{row.full_name},{row.count}\n"  
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=users_stat.csv; charset=utf-8"}
        )
    
    return render_template('logs/usersStat.html', logs=stats)