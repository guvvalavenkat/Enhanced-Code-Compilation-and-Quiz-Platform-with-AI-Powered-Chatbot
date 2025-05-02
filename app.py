from models import User, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO


bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    from routes.chat import chat
    app.register_blueprint(chat)
    import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('GEMINI_API_KEY')


    db.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth
    from routes.compiler import compiler
    from routes.student import student
    from routes.faculty import faculty
    from routes.admin import admin

    app.register_blueprint(auth, url_prefix='')
    app.register_blueprint(compiler, url_prefix='/compiler')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(faculty, url_prefix='/faculty')
    app.register_blueprint(admin, url_prefix='/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)
