from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class WaveForm(FlaskForm):
    wave_content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
