from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm, Form
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import render_form
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
import smtplib

app = Flask(__name__)
app.config['SECRET_KEY'] = "ciouasbocaboxoanxa"
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

# current_user.is_authenticated()

class Base(DeclarativeBase):
    pass


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

EMAIL = "marcelseremak5@gmail.com"
PASSWORD = "yhfu vsbh gcdo imsk"

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    points: Mapped[str] = mapped_column(Text, nullable=False)

class Project(db.Model):
    __tablename__ ="projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_for_user: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    language: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)



with app.app_context():
    db.create_all()






@app.route("/")
def starting_page():
    return render_template("homepage.html", current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for("starting_page", current_user=current_user))
        return redirect(url_for("starting_page", current_user=current_user))

    return render_template("login.html", form=form, current_user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = generate_password_hash(form.password.data,method='pbkdf2:sha256',salt_length=8)
        new_user = User(
            name=name,
            email=email,
            password=password,
            points=0
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("starting_page", current_user=current_user))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("starting_page", current_user=current_user))


@login_required
@app.route("/random_project")
def random_project():
    return render_template("random-project.html", current_user=current_user)


@login_required
@app.route("/profile")
def profile():
    return render_template("profile.html", current_user=current_user)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(EMAIL, PASSWORD)
        connection.sendmail(EMAIL, EMAIL, email_message)


if __name__ == "__main__":
    app.run(debug=True)