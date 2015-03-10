#!flask/bin/python
from flask import render_template, flash, \
    redirect, url_for, request, g
from flask.ext.login import current_user, login_required
from app import db, lm
from ..form import LoginForm
from config import MONKEYS_PAGE
from ..model import Users
from .import layout

@lm.user_loader
def load_user(id):
    return Users.query.get(int(id))


@layout.before_request
def before_request():
    g.user = current_user


@layout.route('/')
def home():
    return render_template('index.html')


@layout.route('/user/<int:page>', methods=['GET', 'POST'])
def user(page=1, sort='normal'):
    user = g.user
    # condition to sort base on ascending
    if request.args.get('sort') == 'asc':
            sortBy = 'asc'
            monkey = Users.query.order_by(Users.name.asc()).\
                paginate(page, MONKEYS_PAGE)
            flash('Monkeys sort by the name!')

    elif request.args.get('sort') == 'friendnum':
        sortBy = 'friendnum'
        # friends are users as well, so need alias
        friend = db.aliased(Users)
        # construct subquery for use in final query
        sub = db.session.query(Users.id, db.func.count(friend.id).label('fn')).\
            join(friend, Users.friends).group_by(Users.id).subquery()
        monkey = Users.query.join(sub, sub.c.id == Users.id).order_by(sub.c.fn.desc()).\
            paginate(page, MONKEYS_PAGE)
        flash('Monkeys  sort by the Friend number!')

    # condition to sort base on bestfriend name
    elif request.args.get('sort') == 'bf':
        sortBy = 'bf'
        friend = db.aliased(Users)
        sub = db.session.query(
            Users.name, friend.name.label('fn')).\
            join(friend, Users.is_bestfriend).group_by(Users.name).\
            group_by('fn').subquery()
        monkey = Users.query.join(sub, sub.c.name == Users.name).\
            order_by(sub.c.fn.asc()).paginate(page, MONKEYS_PAGE, False)
        flash('Monkeys  sort by the bestFriend name!')
    # condition to sort base on normal
    else:
        sortBy = 'normal'
        monkey = Users.query.paginate(page, MONKEYS_PAGE, False)
    return render_template('Users.html',
                           user=user,
                           title='Home',
                           monkey=monkey,
                           sortBy=sortBy
                           )


@layout.route('/new', methods=['GET', 'POST'])
def new():
    """add a new monkey."""
    form = LoginForm(request.form)
    try:
        if request.method == 'POST'and form.validate_on_submit():
            name = form.name.data,
            email = form.email.data,
            age = form.age.data
            user = Users(name=name, email=email, age=age)
            db.session.add(user)
            db.session.commit()
            flash("User was added successfully.", format(name))
            return redirect(url_for('layout.user', page=1, sortby='normal'))
    except:
        flash("Error is found. The user already registerd to the system!")
    return render_template('new.html', form=form)


# Edit monkey information
@layout.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    user = Users.query.get_or_404(id)
    form = LoginForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.age = form.age.data
        db.session.add(user)
        db.session.commit()
        flash("You have been updated the profile")
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    else:  # If the form does not have all fields that are required
        return render_template('edit.html', form=form, id=id)


# delete the monkey
@layout.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    """remove monkey"""
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("{0} is removed!".format(user.name))
    return redirect(url_for("layout.user", page=1, sortby='normal'))


# show profileof each monkey
@layout.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    user = Users.query.get(id)
    return render_template('profile.html', id=id, user=user)


# freinds
@layout.route('/friend/<name>', methods=['POST', 'GET'])
@login_required
def friend(name):
    user = Users.query.filter_by(name=name).first()
    if user is None:
        flash('User %s not found.' % name)
        return redirect(url_for('layout.user'))
    if user == g.user:
        flash('You can\'t Friend yourself!')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    u = g.user.be_friend(user)
    if u is None:
        flash('You have been Friend with ' + name + '.')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    db.session.add(u)
    db.session.commit()
    flash('You are now Friend with ' + name + '!')
    return redirect(url_for('layout.user', page=1, sortby='normal'))


# unfriend
@layout.route('/unfriend/<name>', methods=['GET', 'DELETE'])
@login_required
def unfriend(name):
    user = Users.query.filter_by(name=name).first()
    if user is None:
        flash('User %s not found.')
        return redirect(url_for('home'))
    if user == g.user:
        flash('You can\'t unFriend yourself!')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    u = g.user.unfriend(user)
    if u is None:
        flash('Cannot unFriend ' + name + '.')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    db.session.add(u)
    db.session.commit()
    flash('You are not Friend with ' + name + '!')
    return redirect(url_for('layout.user', page=1, sortby='normal'))


# best_freinds
@layout.route('/bestFriend/<name>', methods=['GET', 'POST'])
@login_required
def bestFriend(name):
    user = Users.query.filter_by(name=name).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t Best Friend yourself!')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    u = g.user.be_bestfriend(user)
    if u is None:
        flash('Cannot be best Friend ' + name + '.')
        return redirect(url_for('layout.user', page=1, sortby='normal'))
    db.session.add(u)
    db.session.commit()
    flash('You are now BestFriend with ' + name + '!')
    return redirect(url_for('layout.user', page=1, sortby='normal'))
