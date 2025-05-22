from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py') 
app.secret_key = '70ec4882d43c8c739b5934540e8e62bd2bee5b2d4fd970691cc1c1ce826a77f5'
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Войдите в аккаунт для доступа к материалам сайта)'
login_manager.login_message_category = 'warning'

def get_users():
    return [
        {
            'id': '1',
            'login': 'user',
            'password': 'qwerty'
        }
    ]

@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if str(user_id) == str(user['id']):
            return User(user['id'], user['login'])
    return None

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login
    def get_id(self):
        return str(self.id)
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    
    if request.method == 'POST':
        login = request.form.get('username')
        password = request.form.get('password')
        check = request.form.get('remember_me') == 'on'
        if login and password:
            for user in get_users():
                if user['login'] == login and user['password'] == password:
                    user = User(user['id'], user['login'])
                    login_user(user, remember = check)
                    flash('Вы успешно аутентифицированы!', 'success')
                    session['greeting'] = "Добро пожаловать, " + login + "!"
                    return redirect(next_page or url_for('index'))
            return render_template('login.html', error="Введены неверные данные!")
        return render_template('login.html', error="Необходимо заполнить все поля!")
    return render_template('login.html')
    

    
@app.route('/visitscounter')
def visitscounter():
    # Увеличиваем счетчики
    if current_user.is_authenticated:
        user_key = f"user_{current_user.id}_visits"
        session[user_key] = session.get(user_key, 0) + 1
        session['counter'] = session.get('counter', 0) + 1
    else:
        session['counter'] = session.get('counter', 0) + 1

    # Явно указываем, что сессия изменена
    session.modified = True

    return render_template('visitscounter.html')

@app.route('/secretpage')
@login_required
def secretpage():
    return render_template('secretpage.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))