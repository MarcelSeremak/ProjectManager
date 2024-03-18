import random
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, AddNewProject, RandomProject
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import render_form
from flask_login import UserMixin, login_user, login_required, LoginManager, current_user, logout_user
import os
import smtplib
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")


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

EMAIL = "YOUR_EMAIL"
PASSWORD = "PASSWORD_FOR_YOUR_EMAIL"


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
    priority: Mapped[int] = mapped_column(Integer, nullable=False)

class RandomIdea(db.Model):
    __tablename__ = "random_ideas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)




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
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        send_email(name, email, subject, message)
        return redirect(url_for("starting_page"))
    else:
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


@app.route("/random_project", methods=["POST", "GET"])
@login_required
def random_project():
    idea_user = User.query.filter_by(id=current_user.id).first()
    if int(idea_user.points) >= 50:
        idea_user.points = int(idea_user.points) - 50
        db.session.commit()
        idea = db.session.execute(db.select(RandomIdea).where(RandomIdea.id == str(random.randint(1, 199)))).scalar()
        return render_template("random-project.html", current_user=current_user, idea=idea)
    else:
        return redirect(url_for("profile"))


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    projects_for_user = db.session.execute(db.select(Project).where(Project.id_for_user == current_user.id)).scalars().all()
    return render_template("profile.html", current_user=current_user, points=int(current_user.points),
                           projects_for_user=projects_for_user)


@app.route("/add_new_project", methods=["POST", "GET"])
@login_required
def add_new_project():
    form = AddNewProject()
    if form.validate_on_submit():
        project = Project(
            id_for_user=current_user.id,
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            language=form.language.data
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("add_new_project.html", form=form, current_user=current_user)


@app.route("/delete", methods=["POST", "GET"])
@login_required
def delete():
    task_id = request.args.get("id")
    task_to_delete = db.session.execute(db.select(Project).where(Project.id == task_id)).scalar()
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("profile"))


@app.route("/accept", methods=["POST", "GET"])
@login_required
def accept():
    form = RandomProject()
    if form.validate_on_submit():
        title = request.args.get("title")
        project = Project(
            id_for_user=current_user.id,
            title=title,
            description=form.description.data,
            priority=form.priority.data,
            language=form.language.data
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("edit_random_idea.html", current_user=current_user, form=form)



@app.route("/decline")
@login_required
def decline():
    return redirect(url_for("profile"))


@app.route("/done", methods=["POST", "GET"])
@login_required
def done():
    task_id = request.args.get("id")
    user_id = request.args.get("user_id")
    task_done = db.session.execute(db.select(Project).where(Project.id == task_id)).scalar()
    db.session.delete(task_done)
    db.session.commit()
    task_user = User.query.filter_by(id=user_id).first()
    print(task_user)
    print(task_user.points)
    task_user.points = int(task_user.points) + 10
    db.session.commit()
    return redirect(url_for("profile"))


def send_email(name, email, subject, message):
    email_message = f"Subject:{subject}\n\nName: {name}\nEmail: {email}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(EMAIL, PASSWORD)
        connection.sendmail(EMAIL, EMAIL, email_message)


if __name__ == "__main__":
    app.run(debug=True)