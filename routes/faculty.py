import socketio
from flask import Blueprint, request, jsonify, render_template, flash, url_for, redirect, session
from flask_bcrypt import check_password_hash
from flask_login import login_required, current_user, login_user

from models import db, Feedback, User, Quiz, QuizQuestion, Question, Submission, QuizSubmission, TestCase
from app import socketio

faculty = Blueprint("faculty", __name__)


@faculty.route("/faculty-login", methods=["GET", "POST"])
def faculty_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        faculty = User.query.filter_by(email=email, role="faculty").first()
        if faculty and check_password_hash(faculty.password, password):
            login_user(faculty)
            session["user_id"] = faculty.id
            session["role"] = "faculty"

            flash("Faculty Login Successful!", "success")
            return redirect(url_for("faculty.dashboard"))

        flash("Invalid Faculty Credentials", "danger")

    return render_template("auth/faculty_login.html")


@faculty.route("/feedback", methods=["POST"])
def send_feedback():
    data = request.json
    feedback = Feedback(student_id=data["student_id"], faculty_id=data["faculty_id"], message=data["message"])
    db.session.add(feedback)
    db.session.commit()

    socketio.emit("new_feedback", {"message": data["message"]}, broadcast=True)
    return jsonify({"message": "Feedback sent"})


@faculty.route("/give_feedback", methods=["POST"])
@login_required
def give_feedback():
    student_id = request.form['student_id']
    message = request.form['message']
    feedback = Feedback(student_id=student_id, faculty_id=current_user.id, message=message)
    db.session.add(feedback)
    db.session.commit()
    flash("Feedback submitted successfully!", "success")
    return redirect(url_for('faculty.dashboard'))


@faculty.route('/dashboard')
@login_required
def dashboard():
    if session.get("role") != "faculty":
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.login"))
    quizzes = Quiz.query.filter_by(faculty_id=current_user.id).all()
    coding_questions = Question.query.filter_by(faculty_id=current_user.id, question_type="Coding").all()
    quiz_questions = QuizQuestion.query.join(Quiz).filter(Quiz.faculty_id == current_user.id).all()
    students = User.query.filter_by(role='student').all()
    student_progress = {student.id: {"completed_quizzes": 0, "solved_questions": 0} for student in students}
    progress_data = db.session.query(
        User.id,
        db.func.count(QuizSubmission.id).label("completed_quizzes"),
        db.func.count(Submission.id).label("solved_questions")
    ).outerjoin(QuizSubmission, QuizSubmission.student_id == User.id
                ).outerjoin(Submission, Submission.student_id == User.id
                            ).filter(User.role == 'student').group_by(User.id).all()
    for student_id, completed_quizzes, solved_questions in progress_data:
        student_progress[student_id]["completed_quizzes"] = completed_quizzes
        student_progress[student_id]["solved_questions"] = solved_questions
    print(coding_questions)
    print("Quizzes fetched:", quizzes)
    print("Coding questions fetched:", coding_questions)

    return render_template('faculty/dashboard.html',
                           quizzes=quizzes,
                           quiz_questions=quiz_questions,
                           coding_questions=coding_questions,
                           students=students,
                           student_progress=student_progress)


@faculty.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']
        new_quiz = Quiz(title=title, faculty_id=current_user.id)
        db.session.add(new_quiz)
        db.session.commit()

        questions = request.form.getlist('questions[]')
        correct_answers = request.form.getlist('correct_answers[]')

        for i, question_text in enumerate(questions):
            options = request.form.getlist(f'options_{i}[]')

            correct_answer_index = correct_answers[i]
            correct_answer_text = options[ord(correct_answer_index) - ord('A')]

            new_question = QuizQuestion(
                quiz_id=new_quiz.id,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer_text
            )
            db.session.add(new_question)

        db.session.commit()
        flash("Quiz created successfully!", "success")
        return redirect(url_for('faculty.dashboard'))

    return render_template('faculty/quiz.html')


@faculty.route('/track-progress/<int:student_id>')
@login_required
def track_progress(student_id):
    student = User.query.get_or_404(student_id)

    completed_quizzes = db.session.query(Quiz, QuizSubmission.score).join(
        QuizSubmission, QuizSubmission.quiz_id == Quiz.id
    ).filter(QuizSubmission.student_id == student_id).all()

    solved_questions = db.session.query(Question, Submission.language).join(
        Submission, Submission.question_id == Question.id
    ).filter(Submission.student_id == student_id).all()

    return render_template('faculty/track_progress.html',
                           student=student,
                           completed_quizzes=completed_quizzes,
                           solved_questions=solved_questions)


@faculty.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
    print(f"Debug: Found {len(questions)} questions for quiz_id {quiz_id}")
    return render_template('faculty/view_quiz.html', quiz=quiz, questions=questions)


@faculty.route('/post-question', methods=['GET', 'POST'])
@login_required
def post_question():
    if request.method == 'POST':
        title = request.form.get('title')
        questions = request.form.get('content')

        if not title or not questions:
            flash("Title and question details are required!", "danger")
            return redirect(url_for('faculty.post_question'))

        new_question = Question(
            student_id=None,
            faculty_id=current_user.id,
            title=title,
            question_type="Coding",
            questions=questions
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Coding question posted successfully!", "success")
        return redirect(url_for('faculty.dashboard'))

    return render_template('faculty/post_question.html')


@faculty.route('/view-student-code/<int:student_id>')
@login_required
def view_student_code(student_id):
    """View all coding submissions of a student."""
    student = User.query.get_or_404(student_id)
    submissions = Submission.query.filter_by(student_id=student_id).all()

    return render_template('faculty/view_student_code.html', student=student, submissions=submissions)


@faculty.route('/view-student-quiz/<int:student_id>')
@login_required
def view_student_quiz(student_id):
    """View quiz results of a student."""
    student = User.query.get_or_404(student_id)
    quiz_results = QuizSubmission.query.filter_by(student_id=student_id).all()

    return render_template('faculty/view_student_quiz.html', student=student, quiz_results=quiz_results)


@faculty.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if question.faculty_id != current_user.id:
        flash("You can only edit your own questions.", "danger")
        return redirect(url_for('faculty.dashboard'))

    if request.method == 'POST':
        question.title = request.form['title']
        question.questions = request.form['content']
        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('faculty.dashboard'))

    return render_template('faculty/edit_question.html', question=question)


@faculty.route('/edit-quiz-question/<int:quiz_question_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz_question(quiz_question_id):
    quiz_question = QuizQuestion.query.get_or_404(quiz_question_id)

    if quiz_question.quiz.faculty_id != current_user.id:
        flash("You can only edit your own quiz questions.", "danger")
        return redirect(url_for('faculty.dashboard'))

    if request.method == 'POST':
        quiz_question.question_text = request.form['question_text']
        quiz_question.correct_answer = request.form['correct_answer']
        quiz_question.options = request.form.getlist('options[]')
        db.session.commit()
        flash("Quiz question updated successfully!", "success")
        return redirect(url_for('faculty.dashboard'))

    return render_template('faculty/edit_quiz_question.html', quiz_question=quiz_question)


@faculty.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.faculty_id != current_user.id:
        flash("You can only delete your own quizzes.", "danger")
        return redirect(url_for('faculty.dashboard'))

    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('faculty.dashboard'))


@faculty.route('delete-question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.faculty_id != current_user.id:
        flash("You can only delete your own quizzes.", "danger")
        return redirect(url_for('faculty.dashboard'))
    db.session.delete(question)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('faculty.dashboard'))


@faculty.route('/faculty/question/<int:question_id>/testcases', methods=['GET', 'POST'])
def add_testcase(question_id):
    question = Question.query.get_or_404(question_id)
    coding_questions = Question.query.all()

    if request.method == 'POST':
        input_data = request.form['input_data'].strip()
        expected_output = request.form['expected_output'].strip()

        new_test = TestCase(
            question_id=question.id,
            input_data=input_data,
            expected_output=expected_output
        )
        db.session.add(new_test)
        db.session.commit()
        flash('Test Case added successfully!', 'success')
        return redirect(url_for('faculty.add_testcase', question_id=question.id))

    test_cases = TestCase.query.filter_by(question_id=question.id).all()

    return render_template(
        'faculty/manage_testcases.html',
        test_cases=test_cases,
        coding_questions=coding_questions,
        selected_question=question
    )


@faculty.route('/faculty/testcases/<int:question_id>', methods=['GET', 'POST'])
def manage_testcases(question_id):
    """ Add and manage test cases for a specific question """
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        input_data = request.form['input_data'].strip()
        expected_output = request.form['expected_output'].strip()

        new_testcase = TestCase(question_id=question_id, input_data=input_data, expected_output=expected_output)
        db.session.add(new_testcase)
        db.session.commit()

        flash('Test Case Added Successfully!', 'success')
        return redirect(url_for('faculty.manage_testcases', question_id=question_id))

    test_cases = TestCase.query.filter_by(question_id=question_id).all()

    return render_template(
        'faculty/manage_testcases.html',
        question=question,
        test_cases=test_cases,
        coding_questions=Question.query.all()
    )


@faculty.route('/faculty/testcases/delete/<int:testcase_id>', methods=['DELETE'])
def delete_testcase(testcase_id):
    """ Delete a specific test case """
    testcase = TestCase.query.get_or_404(testcase_id)
    question_id = testcase.question_id
    db.session.delete(testcase)
    db.session.commit()

    flash('🗑 Test Case Deleted Successfully!', 'danger')
    return jsonify({"message": "Test Case Deleted"}), 200
