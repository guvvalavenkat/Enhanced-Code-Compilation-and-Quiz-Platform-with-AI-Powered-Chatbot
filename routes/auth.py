from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required
from app import db
from flask_bcrypt import check_password_hash, generate_password_hash

from models import User

auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    return render_template('home.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.role == 'pending':
                flash("Your account is awaiting approval.", "warning")
                return redirect(url_for('auth.login'))
            login_user(user)

            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'faculty':
                return redirect(url_for('faculty.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))

        flash("Invalid email or password!", "danger")
        print(user)

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    """ Logout user and clear session """
    logout_user()
    flash("Successfully Logged Out!", "success")
    return redirect(url_for("auth.login"))
