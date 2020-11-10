from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, InputRequired, ValidationError, Length
from tidewave.models import Posts
from sqlalchemy import func


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=100)])
    link = StringField('Link', validators=[Length(max=100)])
    logo = FileField('Project Logo', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    postimages = MultipleFileField('Upload image(s)', validators=[FileAllowed(['jpg', 'png'])])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

    def validate_posttitle(self, posttitle):
        post = Posts.query.filter(func.lower(Posts.title) == func.lower(posttitle.data)).first()
        if post:
            raise ValidationError('Post title is not available.')


class SearchForm(FlaskForm):
    keyword = StringField('Keyword', validators=[DataRequired()])
    submitsearch = SubmitField('Search')


class PostEditForm(FlaskForm):
    posttitle = StringField('Title', validators=[DataRequired()])
    postdescription = StringField('Description', validators=[DataRequired(), Length(max=100)])
    postlink = StringField('Link')
    postlogo = FileField('Replace logo', validators=[FileAllowed(['jpg', 'png'])])
    postimages = MultipleFileField('Replace image(s)', validators=[FileAllowed(['jpg', 'png'])])
    postcontent = TextAreaField('Content', validators=[DataRequired()])
    postsubmit = SubmitField('Post')
