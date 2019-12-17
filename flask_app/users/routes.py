from flask import render_template, url_for, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from flask_app import db, bcrypt
from flask_app.models import User, Post
from flask_app.users.forms import RegistrationForm, LoginForm, UpdateForm
from wtforms.validators import ValidationError

users = Blueprint("users", __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            form.validate_user(form.username.data)
            form.validate_email(form.email.data)
            hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            user = User(username=form.username.data, email=form.email.data, password=hashed)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('users.login'))
        except ValidationError as ve:
            print(ve)

    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    try:
        if form.validate_on_submit():
            form.validate_username(form.username)
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('users.account'))
    except ValidationError as ve:
        print(ve)

    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()

    if form.validate_on_submit():
        try:
            current_user.username = form.username.data

            db.session.commit()

            return redirect(url_for('users.account'))
        except ValidationError as ve:
            print(ve)
    elif request.method == 'GET':
        form.username.data = current_user.username

    return render_template('account.html', title='Account', form=form)
