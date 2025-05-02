from flask import Blueprint, request, jsonify
from models import db, Question

bp = Blueprint("questions", __name__)


@bp.route("/post-question", methods=["POST"])
def post_question():
    data = request.json
    new_question = Question(title=data["title"], description=data["description"], type=data["type"],
                            user_id=data["user_id"])
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Question posted"}), 201


@bp.route("/questions", methods=["GET"])
def get_questions():
    questions = Question.query.all()
    return jsonify([{"id": q.id, "title": q.title, "description": q.description, "type": q.type} for q in questions])
