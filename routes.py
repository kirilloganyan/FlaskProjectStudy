from datetime import datetime
from app import app
from flask import render_template, request, redirect, flash, url_for
from forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app import mail
from flask_mail import Message


from logic import get_concate_username
from models import User
from oauth import OAuthSignIn


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/users')
def show_all_users():
    all_users = User.query.all()
    return render_template('showAllUsers.html', users=all_users)

@app.route('/')
def index():  # put application's code here
    posts = [
        {
            'author':{'username':'Test1'},
            'head':"Что-то про моду",
            'body':"Большой текст про лук и другие модные веши"
        },
        {
            'author':{'username': 'Drozdov'},
            'head': "Что-то про животных",
            'body': "Этот дикий программист медленно подходит знакомиться с flask-ом"
        },
        {
            'author':{'username': 'Солженицын'},
            'head': "Что-то там про ГУЛАГ",
            'body': "Книга про то, как там плохо"
        }
    ]
    return render_template('index.html', user=current_user, posts=posts)

def send_mail(adress):
    with mail.connect() as conn:
        msg = Message("Test message", sender="flasktest123@yandex.ru", recipients=[adress])
        msg.body = "Hello boddy"
        msg.html = "<h1>Test</h1>"
        conn.send(msg)
        print("test")


@app.route('/hello')
@login_required
def hello():
    username = request.args.get('name')
    age = request.args.get('age')
    return render_template('hello.html', name=username, age=age)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect((url_for("index")))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect((url_for("index")))
        login_user(user, remember=True)
        return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect((url_for("index")))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats! Registration complete!')
        return redirect((url_for('login')))
    return render_template("registration.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect((url_for("index")))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('login'))
    oauth = OAuthSignIn.get_provider(provider)
    user_id, token = oauth.callback()
    if user_id is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        username = get_concate_username(token, user_id)

        user = User(user_id=user_id, token=token, username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user, True)
    return redirect(url_for('login'))

@app.route('/user/<username>')
@login_required
def user(username):
    return render_template('user.html', user=current_user)

@app.route('/add_friend/<username>')
def add_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.add_friend(user)
        db.session.commit()
    all_users = User.query.all()
    return render_template('showAllUsers.html', users=all_users)


@app.route('/remove_friend/<username>')
def remove_friend(username):
    user = User.query.filter_by(username=username).first()
    if not user is None:
        current_user.delete_friend(user)
        db.session.commit()
    all_users = User.query.all()
    return render_template('showAllUsers.html', users=all_users)
