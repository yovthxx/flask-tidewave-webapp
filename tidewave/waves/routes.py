from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from tidewave import db
from tidewave.models import Tags, Posts, Waves, Tides
from tidewave.waves.forms import WaveForm

waves = Blueprint('waves', __name__)

@waves.route('/dir/<tag>/project/<post_title>/<int:stage>/new_wave', methods=['GET', 'POST'])
@login_required
def new_wave(tag,post_title,stage):
    tag = Tags.query.filter_by(tag=tag).first()
    post = Posts.query.filter_by(title=post_title, tag_id=tag.id).first_or_404()
    if stage>0:
        tide = Tides.query.filter_by(post_id=post.id, stage=stage).first_or_404()
    waveform = WaveForm()
    if waveform.validate_on_submit():
        new_wave = Waves(content = waveform.wave_content.data, post_id=post.id, user_id=current_user.id, stage=stage)
        db.session.add(new_wave)
        subs = post.subscribers
        for sub in subs:
            sub.subscriber.notify_wave(post, new_wave)
        db.session.commit()
        flash('A wave posted!', 'success')
        if request.referrer:
            return redirect(request.referrer)
        return redirect(url_for('posts.post', tag=tag.tag, post_title=post.title))