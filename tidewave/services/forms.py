from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class TagForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tag = StringField('Tag', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')
