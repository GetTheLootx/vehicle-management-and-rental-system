from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import datetime
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "=+@02(+993nyoog&o1mcsv5m46!&rq!2l%i8)7u+r09nt8_6"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    app.config['MAIL_SERVER'] = 'smtp.seznam.cz'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'nakouli@seznam.cz'
    app.config['MAIL_PASSWORD'] = 'Revolucni292'
    app.config['MAIL_USE_SSL'] = True

    db.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, customer, pujceno, trailer, back

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
