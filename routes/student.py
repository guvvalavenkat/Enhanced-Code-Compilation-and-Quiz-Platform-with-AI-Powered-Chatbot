from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_bcrypt import check_password_hash
from flask_login import login_required, current_user, login_user
from models import db, Question, Quiz, Feedback, QuizSubmission, QuizQuestion, Submission, User

student = Blueprint('student', __name__)


@student.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        student = User.query.filter_by(email=email, role="student").first()
        if student and check_password_hash(student.password, password):
            login_user(student, remember=True)

            print("Session Data:", session)

            flash("Student Login Successful!", "success")
            return redirect(url_for("student.dashboard"))

        flash("Invalid Student Credentials", "danger")

    return render_template("auth/student_login.html")


@student.route('/dashboard')
@login_required
def dashboard():
    coding_questions = Question.query.filter(
        (Question.question_type == "Coding") &
        ((Question.student_id == current_user.id) | (Question.faculty_id.isnot(None)))
    ).all()

    non_coding_questions = Question.query.filter_by(student_id=current_user.id, question_type="Non-Coding").all()

    solved_questions = {submission.question_id for submission in
                        Submission.query.filter_by(student_id=current_user.id).all()}

    for question in coding_questions:
        question.is_solved = question.id in solved_questions
        question.solved_by = db.session.query(Submission, User.username).join(User).filter(
            Submission.question_id == question.id
        ).first()

    for question in non_coding_questions:
        if question.related_quiz_id is None:
            question.related_quiz_id = Quiz.query.first().id

    all_quizzes = Quiz.query.all()
    completed_quizzes = QuizSubmission.query.filter_by(student_id=current_user.id).all()
    completed_quiz_ids = {submission.quiz_id for submission in completed_quizzes}

    available_quizzes = [quiz for quiz in all_quizzes if quiz.id not in completed_quiz_ids]
    completed_quizzes = [quiz for quiz in all_quizzes if quiz.id in completed_quiz_ids]
    print("Available Quizzes:", available_quizzes)

    feedbacks = Feedback.query.filter_by(student_id=current_user.id).all()

    return render_template('student/dashboard.html',
                           coding_questions=coding_questions,
                           non_coding_questions=non_coding_questions,
                           solved_questions=solved_questions,
                           available_quizzes=available_quizzes,
                           completed_quizzes=completed_quizzes,
                           feedbacks=feedbacks)


@student.route('/take-quiz/<int:quiz_id>', methods=['GET'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
    for question in questions:
        question.options = question.get_options()

    if not questions:
        flash("No questions available for this quiz.", "warning")
    return render_template('student/quiz.html', quiz=quiz, questions=questions)


@student.route('/submit-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
    score = 0

    print(f"Debug: Submitting Quiz - Quiz ID: {quiz.id}, Student ID: {current_user.id}")

    for question in questions:
        selected_answer = request.form.get(f"q{question.id}")
        correct_answer = question.correct_answer.strip().lower()
        print(f"Question: {question.question_text}")
        print(f"Correct Answer: {correct_answer}")
        print(f"Selected Answer: {selected_answer}")

        if selected_answer and selected_answer.strip().lower() == correct_answer:
            score += 1

    print(f"Final Score: {score}")

    new_submission = QuizSubmission(student_id=current_user.id, quiz_id=quiz.id, score=score)
    db.session.add(new_submission)
    db.session.commit()

    flash(f"You scored {score}/{len(questions)}!", "success")
    return redirect(url_for('student.dashboard'))


@student.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        question_type = request.form['question_type']
        content = request.form['content']

        new_question = Question(
            student_id=current_user.id,
            description=description,
            content=content,
            title=title,
            question_type=question_type

        )
        db.session.add(new_question)
        db.session.commit()
        flash("Your question has been posted!", "success")
        return redirect(url_for('student.dashboard'))

    return render_template('student/post_question.html')


@student.route('/solve/<int:question_id>', methods=['GET', 'POST'])
@login_required
def solve(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        code_solution = request.form['code_solution']
        flash("Solution submitted successfully!", "success")
        return redirect(url_for('student.dashboard'))

    return render_template('student/solve_.html', question=question)


@student.route('/submit_solution', methods=['POST'])
@login_required
def submit_solution():
    data = request.get_json()
    code = data.get("code")
    language_id = data.get("language_id")
    language_name = data.get("language_name")
    execution_time = float(data.get("execution_time", 0))
    question_id = data.get("question_id")
    output = data.get("output", "").strip()

    if not (code and language_id and question_id):
        return jsonify({"error": "Missing required data"}), 400

    efficiency = max(0, (1.0 / (execution_time + 0.1)) * 100)

    submission = Submission(student_id=current_user.id, question_id=question_id, code=code, language=language_name,
                            output=output,
                            execution_time=execution_time,
                            efficiency=round(efficiency, 2))
    db.session.add(submission)
    db.session.commit()

    flash("Solution submitted successfully!", "success")
    return jsonify({"message": "Solution submitted successfully!", "execution_time": execution_time,
                    "output": output, "efficiency": efficiency}), 200
