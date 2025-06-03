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
from proj_code.repositories.log_repository import LogRepository

bp = Blueprint('logs', __name__, url_prefix='/logs')
log_repository = LogRepository(db)

@bp.route('/visit_log')
def visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    if current_user.id == 'Администратор':
        logs, total = log_repository.get_all_logs(page, per_page)
    else:
        logs, total = log_repository.get_user_logs(current_user.id, page, per_page)
    return render_template(
        'logs.visit_log.html',
        logs=logs,
        page=page,
        per_page=per_page,
        total=total
    )