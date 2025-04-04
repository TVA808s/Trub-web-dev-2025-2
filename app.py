from flask import Flask, render_template, abort, request, make_response, session, redirect, url_for, flash
from faker import Faker
from flask_login import LoginManager, UserMixin, login_user, login_required

fake = Faker()

app = Flask(__name__)
app.secret_key = 'to_work_with_sessions'
application = app
# app.config['PERMANENT_SESSION_LIFETIME'] = 60
app.config['REMEMBER_COOKIE_DURATION'] = 60*2
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Для доступа требуется авторизация', 'error')
    return redirect(url_for('login', next=request.endpoint))

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    import random
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    try:
        p = posts_list[index]
    except IndexError:
        abort(404)
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/urlp')
def urlp():
    return render_template('URL.html', params=request.args)

@app.route('/headlines')
def headlines():
    return render_template('headlines.html', headers=request.headers)

@app.route('/cookie')
def cookie():
    response = make_response(render_template('cookie.html', cookies=request.cookies))
    if 'self_made' in request.cookies:
        response.delete_cookie('self_made')
    else:
        response.set_cookie('self_made', '999', 20)
    return response

@app.route('/formp', methods=['GET', 'POST'])
def formp():
    form_data = request.form
    return render_template('formp.html', form_data=form_data)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html')

def NumberFormat(number):
    if number == '':
        return 0
    return f'8-{number[0:3]}-{number[3:6]}-{number[6:8]}-{number[8::]}'

@app.route('/telephone', methods=['GET', 'POST'])
def telephone():
    import re
    number = ''
    error=''
    if request.method == 'POST':
        try:
            dirty_phone = request.form.get('phone', '').strip()

            if not re.match(r'^[\d+\s().-]+$', dirty_phone):
                raise Exception('Недопустимый ввод. В номере телефона встречаются недопустимые символы.')
            
            phone = re.sub(r'[^\d+]', '', dirty_phone)

            if re.match(r'^(\+7|8)\d{10}$', phone):
                if phone[0] == '+':
                    phone = phone[2:]
                else:
                    phone = phone[1:]
                number = phone
            
            elif re.match(r'^\d{10}$', phone):
                number = phone
                
            else:
                raise Exception('Недопустимый ввод. Неверное количество цифр.')
            
        except Exception as e:
            error = str(e)
    
    return render_template('telephone.html', phone=NumberFormat(number), error=error)

@app.route('/counter')
def counter():
    session['visited'] = session.get('visited', 0) + 1
    return render_template('counter.html', s=session['visited'])

users = {'user': {'password': 'qwerty'}}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log = request.form.get('login')
        pas = request.form.get('passwd')
        rem = request.form.get('rem') == 'on'
        if log in users and users[log]['password'] == pas:
            user = User(log)
            login_user(user, remember=rem)
            # session.permanent = True
            flash('Вы успешно вошли', 'success')
            next_page = request.form.get('next')
            if next_page:
                return redirect(url_for(next_page))
            else:
                return redirect(url_for('index'))
        else:
            flash('Неверные данные', 'error')
    return render_template('login.html')

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


