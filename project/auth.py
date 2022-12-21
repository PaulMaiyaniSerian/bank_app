from flask import Blueprint,flash, render_template, redirect, url_for, request
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()


    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))


    login_user(user, remember=False)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('register.html')


@auth.route('/signup', methods=['POST'])
# @login_required
def signup_post():

    # code to validate and add user to database goes here
    # if not current_user.is_system_user:
    #     flash("you are not allowed to view this page")
    #     return redirect(url_for('main.index'))
    # check if there are any users
    # then the first becomes system_user
    users = User.query.filter_by()

    if users.count() < 1:
        print("creating admin account")
        admin_email = "admin@gmail.com"
        admin_name = "admin"
        admin_password = "1234"
        admin_user = User(email=admin_email,is_system_user=True,  name=admin_name, password=generate_password_hash(admin_password, method='sha256'))

        # add the new user to the database
        db.session.add(admin_user)
        db.session.commit()
        logout_user()


    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    print(name, '----------------------')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))