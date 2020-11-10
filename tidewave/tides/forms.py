from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length


class TideForm(FlaskForm):
    tide_title = StringField('Title', validators=[DataRequired(), Length(max=250)])
    tide_content = TextAreaField('Content', validators=[DataRequired()])
    tide_images = MultipleFileField('Upload image(s)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class WaveForm(FlaskForm):
    wave_content = StringField('Content', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Post')


class TideEditForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    images = MultipleFileField('Upload image(s)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Edit tide')
