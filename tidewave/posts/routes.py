from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint, jsonify, make_response)
from flask_login import current_user, login_required
from tidewave import db
from tidewave.models import Posts, Tags, Tides, Comments, Replies, Waves, Images
from tidewave.posts.forms import PostForm, SearchForm, PostEditForm
from tidewave.tides.forms import TideForm
from tidewave.posts.utils import save_logo, save_image
from tidewave.comments.forms import CommentForm, ReplyForm
from tidewave.waves.forms import WaveForm
import random
import time
import datetime
from sqlalchemy import func

posts = Blueprint('posts', __name__)


@posts.route('/dir/<tag>/project/new', methods=['GET', 'POST'])
@login_required
def new_post(tag):
    form = PostForm()
    tag = Tags.query.filter_by(tag=tag).first()
    if current_user.timeout_post():
        if form.validate_on_submit():
            logo_file = save_logo(form.logo.data)
            post = Posts(title=form.title.data, link=form.link.data, description=form.description.data, content=form.content.data, author=current_user, tag_id=tag.id, logo_file=logo_file)
            db.session.add(post)
            db.session.commit()
            for image in form.postimages.data:
                filename = save_image(image)
                if filename:
                    new_image = Images(stage=0, filename=filename, post_id=post.id)
                    db.session.add(new_image)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('posts.post', tag=tag.tag, post_title=post.title))
        flash(form.errors)
        return redirect(request.referrer)
    else:
        flash('Please wait 5 minutes before posting another project')
        return redirect(request.referrer)


@posts.route('/dir/<tag>/project/<post_title>', methods=['GET', 'POST'])
def post(tag, post_title):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first_or_404()
    tides = Tides.query.filter_by(post_id=post.id).order_by(Tides.stage).all()
    comments = Comments.query.filter_by(post_id=post.id, stage=0).order_by(Comments.date_posted.desc()).all()
    waves = Waves.query.filter_by(post_id=post.id, stage=0).order_by(Waves.date_posted.desc()).all()
    images = Images.query.filter_by(post_id=post.id, stage=0).all()
    tideform = TideForm()
    commentform = CommentForm()
    replyform = ReplyForm()
    waveform = WaveForm()
    return render_template('post.html', post=post, tides=tides, comments=comments, waves=waves, tideform=tideform, commentform=commentform, replyform=replyform, waveform=waveform, images=images)


@posts.route('/dir/<tag>/project/<post_title>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(tag, post_title):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first_or_404()
    if post.author != current_user:
        abort(403)
    form = PostEditForm()
    if form.validate_on_submit():
        if form.postlogo.data:
            logo_file = save_logo(form.postlogo.data)
            post.logo_file = logo_file
        if form.postimages.data:
            old_images = Images.query.filter_by(post_id=post.id).all()
            for image in form.postimages.data:
                filename = save_image(image)
                if filename:
                    new_image = Images(stage=0, filename=filename, post_id=post.id)
                    db.session.add(new_image)
                    if old_images:
                        for old_image in old_images:
                            db.session.delete(old_image)
                        db.session.commit()
        post.title = form.posttitle.data
        post.desctiption = form.postdescription.data
        post.link = form.postlink.data
        post.content = form.postcontent.data
        db.session.commit()
        flash('Edit successful!', 'success')
        return redirect(url_for('posts.post', tag=tag.tag, post_title=post.title))
    elif request.method == 'GET':
        form.posttitle.data = post.title
        form.postdescription.data = post.description
        form.postcontent.data = post.content
        form.postlink.data = post.link
    return render_template('edit_post.html', form=form, post=post)


@posts.route('/dir/<tag>/project/<post_title>/delete', methods=['GET', 'POST'])
@login_required
def post_delete(tag, post_title):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first()
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/search", methods=['GET', 'POST'])
def search():
    searchform = SearchForm()
    posts = []
    if searchform.validate_on_submit():
        keyword = searchform.keyword.data
        posts = Posts.query.msearch(keyword, fields=['title', 'description', 'content'], limit=10)
        return render_template("search.html", posts=posts, searchform=searchform)
    return render_template("search.html", posts=posts, searchform=searchform)


@posts.route('/load', methods=['GET', 'POST']) #This is a post loading enpoint used for the homepage
def load():
    """ Route to return the posts """
    time.sleep(0.2)
    posts = [i.serialize for i in Posts.query.order_by(Posts.date_posted.desc()).all()] # Custom serializer is built into post db model
    quantity = 15 # How many posts are loaded per request
    if request.args:
        counter = int(request.args.get("c"))  # This value is set directly in the loading scrypt
        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
            # Slice 0 -> quantity from the db
            res = make_response(jsonify(posts[0: quantity]), 200)

        elif counter == len(posts):
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            # Slice counter -> quantity from the db
            res = make_response(jsonify(posts[counter: counter + quantity]), 200)

    return res
