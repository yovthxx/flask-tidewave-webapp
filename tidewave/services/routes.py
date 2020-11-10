from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint, jsonify, make_response)
from flask_login import current_user, login_required
from tidewave import db
from tidewave.models import Posts, Tags

services = Blueprint('services', __name__)

@services.route('/dir/<tag>/project/<post_title>/<action>', methods=['POST'])
@login_required
def subscribe(tag, post_title, action):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first_or_404()
    if action == 'subscribe':
        current_user.subscribe(post)
        db.session.commit()
    elif action == 'unsubscribe':
        current_user.unsubscribe(post)
        db.session.commit()
    return redirect(request.referrer)

# Disable this route in production or update security measures. It is also used in testing
@services.route('/dir/new/<title>/<description>/<tag>', methods=['POST'])
@login_required
def new_dir(title, description, tag):
    if current_user.username == 'testing' or current_user.rank == 'admin':
        newdir = Tags(title=title, description=description, tag=tag)
        db.session.add(newdir)
        db.session.commit()
        return redirect(url_for('main.home'))
    else:
        abort(404)