from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm, Form
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from flask_bootstrap import render_form
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = "ciouasbocaboxoanxa"
Bootstrap(app)


@app.route("/")
def starting_page():
    return render_template("homepage.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("starting_page"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for("starting_page"))

    return render_template("register.html", form=form)


@app.route('/logout')
def logout():
    return redirect(url_for("starting_page"))


@app.route("/random_project")
def random_project():
    return render_template("random-project.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")



if __name__ == "__main__":
    app.run(debug=True)