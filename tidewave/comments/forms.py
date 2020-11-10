from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    comment_content = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ReplyForm(FlaskForm):
    reply_content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')
