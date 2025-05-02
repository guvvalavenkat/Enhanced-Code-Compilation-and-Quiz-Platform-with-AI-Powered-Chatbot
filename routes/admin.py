from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_bcrypt import check_password_hash
from flask_login import login_required, current_user, login_user
from models import db, User, Quiz, Question, Submission, QuizSubmission

admin = Blueprint('admin', __name__)

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'admin' and not current_user.is_admin):
            flash("Access denied! Only admins can access this page.", "danger")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return login_required(wrapper)


@admin.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admin = User.query.filter_by(email=email, role="admin").first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            session["user_id"] = admin.id
            session["role"] = "admin"

            flash("Admin Login Successful!", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid Admin Credentials", "danger")

    return render_template("auth/admin_login.html")


@admin.route('/dashboard')
@admin_required
def dashboard():
    users = User.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()
    submissions = Submission.query.all()
    quiz_submissions = QuizSubmission.query.all()

    return render_template('admin/dashboard.html', users=users, quizzes=quizzes,
                           questions=questions, submissions=submissions,
                           quiz_submissions=quiz_submissions)



@admin.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))


@admin.route('/delete-question/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))


@admin.route('/delete-submission/<int:submission_id>', methods=['POST'])
@admin_required
def delete_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    db.session.delete(submission)
    db.session.commit()
    flash("Submission deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))


@admin.route('/assign-roles')
@login_required
@admin_required
def assign_roles():
    pending_users = User.query.filter_by(role='pending').all()
    return redirect(url_for('admin.dashboard'))


@admin.route('/assign-role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def assign_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form['role']
    if role in ['student', 'faculty']:
        user.role = role
        db.session.commit()
        flash(f"Role updated to {role}.", "success")
    else:
        flash("Invalid role selected.", "danger")
    return redirect(url_for('admin.dashboard'))
