from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from tidewave import db
from tidewave.models import Posts, Tags, Tides, Comments, Waves, Images
from tidewave.tides.forms import TideForm, TideEditForm
from tidewave.posts.utils import save_image
from tidewave.comments.forms import CommentForm, ReplyForm
from tidewave.waves.forms import WaveForm

tides = Blueprint('tides', __name__)


@tides.route('/dir/<tag>/project/<post_title>/<int:stage>', methods=['GET', 'POST'])
def tide(tag, post_title, stage):
    tag = Tags.query.filter_by(tag=tag).first()
    post = Posts.query.filter_by(title=post_title, tag_id=tag.id).first_or_404()
    tide = Tides.query.filter_by(post_id=post.id, stage=stage).first_or_404()
    tides = Tides.query.filter_by(post_id=post.id).order_by(Tides.stage).all()
    comments = Comments.query.filter_by(post_id=post.id, stage=stage).order_by(Comments.date_posted.desc()).all()
    waves = Waves.query.filter_by(post_id=post.id, stage=stage).order_by(Waves.date_posted.desc()).all()
    images = Images.query.filter_by(post_id=post.id, stage=stage).all()
    tideform = TideForm()
    commentform = CommentForm()
    replyform = ReplyForm()
    waveform = WaveForm()
    return render_template('tide.html', post=post, tide=tide, tideform=tideform, tides=tides, comments=comments, waves=waves, commentform=commentform, replyform=replyform, waveform=waveform, images=images)


@tides.route('/dir/<tag>/project/<post_title>/new_tide', methods=['GET', 'POST'])
@login_required
def new_tide(tag, post_title):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag_id=tag.id).first_or_404()
    tideform = TideForm()
    if tideform.validate_on_submit():
        tide = Tides(title=tideform.tide_title.data, content=tideform.tide_content.data, stage=(int(post.stage) + 1), post_id=post.id, tag=tag, user_id=current_user.id)
        db.session.add(tide)
        db.session.commit()
        for image in tideform.tide_images.data:
            filename = save_image(image)
            if filename:
                new_image = Images(stage=tide.stage, filename=filename, post_id=post.id)
                db.session.add(new_image)
        post.stage = (int(post.stage) + 1)
        subs = post.subscribers
        for sub in subs:
            sub.subscriber.notify_tide(post, tide)
        db.session.commit()
        return redirect(url_for('tides.tide', tag=tag.tag, post_title=post.title, stage=post.stage))


@tides.route('/dir/<tag>/project/<post_title>/<int:stage>/edit', methods=['GET', 'POST'])
@login_required
def tide_edit(tag, post_title, stage):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first_or_404()
    tide = Tides.query.filter_by(post_id=post.id, stage=stage).first_or_404()
    if post.author != current_user:
        abort(403)
    form = TideEditForm()
    if form.validate_on_submit():
        if form.images.data:
            old_images = Images.query.filter_by(post_id=post.id, stage=stage).all()
            for image in form.images.data:
                filename = save_image(image)
                if filename:
                    new_image = Images(stage=stage, filename=filename, post_id=post.id)
                    db.session.add(new_image)
                    if old_images:
                        for old_image in old_images:
                            db.session.delete(old_image)
                        db.session.commit()
        tide.title = form.title.data
        tide.content = form.content.data
        db.session.commit()
        flash('Tide edited', 'success')
        return redirect(url_for('tides.tide', tag=tag.tag, post_title=post.title, stage=stage))
    elif request.method == 'GET':
        form.title.data = tide.title
        form.content.data = tide.content
    else:
        flash('ERROR', 'danger')
        return render_template('edit_tide.html', form=form, tide=tide, post=post)
    return render_template('edit_tide.html', form=form, tide=tide, post=post)


@tides.route('/dir/<tag>/project/<post_title>/<int:stage>/delete', methods=['GET', 'POST'])
@login_required
def tide_delete(tag, post_title, stage):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title, tag=tag).first()
    tide = Tides.query.filter_by(post_id=post.id, stage=stage).first_or_404()
    if post.author != current_user:
        abort(403)
    if tide.stage == post.stage:
        db.session.delete(tide)
        post.stage = post.stage - 1
        db.session.commit()
        flash('Your tide has been deleted!', 'success')
        return redirect(url_for('posts.post', tag=tag.tag, post_title=post.title))
    else:
        flash('You can only delete the latest tide.', 'danger')
        return redirect(url_for('posts.post', tag=tag.tag, post_title=post.title))
