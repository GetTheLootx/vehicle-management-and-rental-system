from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")

        user = User.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Přihlášen', category="success")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Heslo je špatně", category="error")
        else:
            flash('Nejste zaregistrováni', category="error")

    return render_template("login.html", user=current_user)


@auth.route("/sign_up", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form.get("name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        name_exists = User.query.filter_by(name=name).first()

        if name_exists:
            flash('Přihlašovací jméno je zabráno, zvolte jiné', category='error')
        elif password1 != password2:
            flash('Hesla se neshodují', category='error')
        elif len(name) < 2:
            flash('přihlašovací jméno je příliš krátké', category="error")
        elif len(password1) < 6:
            flash('Heslo je příliš krátké', category="error")
        else:
            new_user = User(name=name,
                            password=generate_password_hash(password1, 'sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Účet byl založen', category="success")
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
