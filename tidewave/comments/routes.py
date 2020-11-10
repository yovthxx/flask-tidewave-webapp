from flask import flash, redirect, request, Blueprint, url_for
from flask_login import current_user, login_required
from tidewave import db
from tidewave.models import Comments, Replies, Tags, Posts, Users
from tidewave.comments.forms import CommentForm, ReplyForm

comments = Blueprint('comments', __name__)


@comments.route('/dir/<tag>/project/<post_title>/<int:stage>/new_comment', methods=['POST'])
@login_required
def new_comment(tag, post_title, stage):
    commentform = CommentForm()
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title).first_or_404()
    if current_user.timeout_comment() and current_user.timeout_reply(): #spam filter of sort, user posting timeout is set in models.py
        if commentform.validate_on_submit():
            new_comment = Comments(content=commentform.comment_content.data, tag_id=tag.id, user_id=current_user.id, post_id=post.id, stage=stage)
            db.session.add(new_comment)
            db.session.commit()
            flash('You just left a comment!', 'success')
            return redirect(request.referrer + "#comment" + str(new_comment.id)) #every comment generates an anchor, and user is being redirected back straight to the new comment after posting
        flash(commentform.errors)
        return redirect(request.referrer)
    else:
        flash('Please wait a little before posting another comment', 'danger')
        return redirect(request.referrer)


@comments.route('/dir/<tag>/project/<post_title>/<int:stage>/<comment_id>/new_reply', methods=['POST'])
@login_required
def new_reply(tag, post_title, stage, comment_id):
    replyform = ReplyForm()
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title).first_or_404()
    comment = Comments.query.filter_by(id=comment_id).first_or_404()
    if current_user.timeout_comment() and current_user.timeout_reply(): 
        if replyform.validate_on_submit():
            new_reply = Replies(content=replyform.reply_content.data, comment_id=comment.id, tag_id=tag.id, user_id=current_user.id, post_id=post.id, stage=stage)
            db.session.add(new_reply)
            db.session.commit()
            flash('You just left a reply', 'success')
            return redirect(request.referrer + "#comment" + str(comment.id)) 
        flash(replyform.errors)
        return redirect(request.referrer)
    else:
        flash('Please wait a little before posting another comment', 'danger')
        return redirect(request.referrer)


@comments.route('/dir/<tag>/project/<post_title>/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(tag, post_title, comment_id): #delete function is reachable by author by hovering over their comments/replies
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title).first_or_404()
    comment = Comments.query.filter_by(id=comment_id).first_or_404()
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)


@comments.route('/dir/<tag>/project/<post_title>/reply/<int:reply_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_reply(tag, post_title, reply_id):
    tag = Tags.query.filter_by(tag=tag).first_or_404()
    post = Posts.query.filter_by(title=post_title).first_or_404()
    reply = Replies.query.filter_by(id=reply_id).first_or_404()
    db.session.delete(reply)
    db.session.commit()
    return redirect(request.referrer)
