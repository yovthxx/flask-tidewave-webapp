from flask import render_template, request, Blueprint, flash, redirect
from flask_login import current_user
from tidewave import db
from tidewave.models import Posts, Tags
from tidewave.posts.forms import PostForm
from tidewave.posts.utils import save_logo

tags = Blueprint('tags', __name__)


@tags.route('/dir')
def tag_list():
    tags = Tags.query.all()
    return render_template('dir.html', tags=tags)


@tags.route('/dir/<tag>', methods=['GET', 'POST'])
def tag_single(tag):
    form = PostForm()
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    posts = Posts.query.filter_by(tag_id=tag.id).order_by(Posts.date_posted.desc()).all()
    return render_template('tag.html', posts=posts, form=form, tag=tag)
