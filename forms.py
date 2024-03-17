from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AddNewProject(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    language = StringField("Programming Language", validators=[DataRequired()])
    priority = SelectField("Priority", validators=[DataRequired()], choices=[('High Priority', 'High Priority'),
                                                                             ('Medium Priority', 'Medium Priority'),
                                                                             ('Low Priority', 'Low Priority')])
    submit = SubmitField("Add")
