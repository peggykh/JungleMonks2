#!flask/bin/python
from flask import render_template, flash, redirect, \
    session, url_for, request, g
from flask.ext.login import login_user, logout_user, \
    current_user, login_required
from app import login_manager
from app import db, lm
from config import Config
from ..form import LoginForm
from flask.ext.sqlalchemy import Pagination
from config import MONKEYS_PAGE
from ..model import Users
from . import auth
from sqlalchemy import func


@auth.before_request
def before_request():
    g.user = current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # checks if the user is authernticated or not, if yes it skips authentfic.
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('layout.user'))
        # does not allow user to use get method
    if request.method == 'GET':
            return render_template('login.html',
                                   form=form,
                                   title='Login')
    # taking the user submitted data, checking if it exists in the database
    user_in_db = Users.query.filter_by(name=form.name.data.lower()).first()

    # if the username is not wrong
    if user_in_db is not None and user_in_db is not False:
        if form.email.data != user_in_db.email:
            flash('Email is incorrect')
            return redirect(url_for('auth.login'))
        login_user(user_in_db)
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    else:
        flash('Username does not exists')
        return render_template('login.html',
                               form=form,
                               title='Login')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("auth.login"))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
