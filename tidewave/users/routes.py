from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from tidewave import db, bcrypt
from tidewave.models import Users, Posts, Comments, Notifications
from tidewave.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from tidewave.users.utils import save_picture


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created, you can log in now!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You were logged in')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful', 'danger')
    return render_template('login.html', title='Log In', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    return render_template('account.html', form=form)


@users.route('/user/<string:username>')
def user_page(username):
    user = Users.query.filter_by(username=username).first_or_404()
    posts = Posts.query.filter_by(author=user).limit(3)
    comments = Comments.query.filter_by(author=user).order_by(Comments.date_posted.desc()).limit(5)
    return render_template('user_page.html', user=user, posts=posts, comments=comments)


@users.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    new_notifications = Notifications.query.filter_by(user_id=current_user.id, seen=0).all()
    old_notifications = Notifications.query.filter_by(user_id=current_user.id, seen=1).all()
    for note in new_notifications:
        note.seen = 1
    db.session.commit()
    return render_template('inbox.html', new=new_notifications, old=old_notifications)


@users.route('/inbox/clear')
@login_required
def inbox_clear():
    notifications = Notifications.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(request.referrer)
