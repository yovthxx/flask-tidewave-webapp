from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from tidewave.models import Users
from sqlalchemy import func


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=18)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter(func.lower(Users.username) == func.lower(username.data)).first()
        if user:
            raise ValidationError('Username is not available.')

    def validate_email(self, email):
        user = Users.query.filter(func.lower(Users.email) == func.lower(email.data)).first()
        if user:
            raise ValidationError('Email is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=16)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=18)])
    bio = TextAreaField('Bio', validators=[Length(min=0, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter(func.lower(Users.username) == func.lower(username.data)).first()
            if user:
                raise ValidationError('Username is not available.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter(func.lower(Users.email) == func.lower(email.data)).first()
            if user:
                raise ValidationError('Email is already registered.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter(func.lower(Users.email) == func.lower(email.data)).first()
        if user is None:
            raise ValidationError('No account found.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
