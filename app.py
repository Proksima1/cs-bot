import datetime
from multiprocessing import Process
from flask import Flask, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm
from bot import *

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/')
def main():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    return render_template('main.html', title='Авторизация | Админ-панель', form=form)


@app.route('/start_bot', methods=['GET'])
def start_bot():
    bot_process = Process(target=start_executor)
    bot_process.start()
    bot_process.kill()
    pid = bot_process.pid
    return f'{pid}'


@app.route('/auth', methods=['POST'])
def auth():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True, duration=datetime.timedelta(days=30))
            return jsonify({"success": True, "url": "/home"})
        else:
            return jsonify({"success": False, "message": "Неправильная почта или пароль."})
    else:
        return jsonify({"success": False, "message": 'Что-то пошло не так...'})


@login_required
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', title='Главная | Админ-панель')


@login_required
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main'))


def start_executor():
    executor.start_polling(dp, skip_updates=True)


def startup():
    db.create_all()
    if not User.query.filter(User.email == 'konstant.2015b@mail.ru').first():
        user = User()
        user.email = 'konstant.2015b@mail.ru'
        user.set_password('12')
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    startup()
    app.run('0.0.0.0', threaded=True)
    # app.run()