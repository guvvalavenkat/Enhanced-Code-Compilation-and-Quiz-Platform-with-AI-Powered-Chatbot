import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10),  default='pending')
    
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def is_real_admin(self):
        return self.role == 'admin' or self.is_admin


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    questions = db.Column(db.Text, nullable=False)
    related_quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id], backref='questions')
    faculty = db.relationship('User', foreign_keys=[faculty_id], backref='faculty_questions')
    related_quiz = db.relationship('Quiz', backref='questions')


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.Text)
    language = db.Column(db.String(50))
    output = db.Column(db.String(2500))
    execution_time = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("User", backref="submissions")
    question = db.relationship("Question", backref="submissions")


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id], backref='received_feedback')
    faculty = db.relationship('User', foreign_keys=[faculty_id], backref='given_feedback')


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship("User", backref="quizzes")



class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)
    correct_answer = db.Column(db.String(100), nullable=False)
    quiz = db.relationship('Quiz', backref='quiz_questions')

    def get_options(self):
        """Return options as a list."""
        return json.loads(self.options) if isinstance(self.options, str) else self.options


class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("User", backref="quiz_submissions")
    quiz = db.relationship("Quiz", backref="quiz_submissions")


class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)

    question = db.relationship('Question', backref=db.backref('test_cases', lazy=True))
