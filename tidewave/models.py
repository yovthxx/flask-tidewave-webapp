from tidewave import db, login_manager, moment
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
from whoosh.analysis import RegexTokenizer, Filter
from whoosh.fields import TEXT

#filter included to enable case insensitive search
class CaseSensitivizer(Filter):
    def __call__(self, tokens):
        for t in tokens:
            yield t

            raw_text = t.text
            for i in range(len(raw_text) - 2):
                t.text = raw_text[:3 + i]
                yield t

            text = raw_text.lower()
            if text == t.text:
                continue

            for i in range(len(text) - 2):
                if text[:3 + i] != raw_text[:3 + i]:
                    t.text = text[:3 + i]
                    yield t


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(18), unique=True, nullable=False)
    rank = db.Column(db.String(15), nullable=False, default='user')
    email = db.Column(db.String(35), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(200), nullable=True)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Posts', backref='author', lazy=True, cascade="all, delete", passive_deletes=True)
    tides = db.relationship('Tides', backref='author', lazy=True, cascade="all, delete", passive_deletes=True)
    waves = db.relationship('Waves', backref='author', lazy=True, cascade="all, delete", passive_deletes=True)
    comments = db.relationship('Comments', backref='author', lazy=True, cascade="all, delete", passive_deletes=True)
    replies = db.relationship('Replies', backref='author', lazy=True, cascade="all, delete", passive_deletes=True)
    subscriptions = db.relationship('Subscriptions', backref='subscriber', lazy=True, cascade="all, delete", passive_deletes=True)
    notifications = db.relationship('Notifications', backref='user', lazy=True, cascade="all, delete", passive_deletes=True)

    #subscription methods
    def subscribe(self, post):
        if not self.follows_post(post):
            sub = Subscriptions(user_id=self.id, post_id=post.id)
            db.session.add(sub)

    def unsubscribe(self, post):
        if self.follows_post(post):
            Subscriptions.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def follows_post(self, post):
        return Subscriptions.query.filter(
            Subscriptions.user_id == self.id,
            Subscriptions.post_id == post.id).count() > 0

    #notification methods
    def notify_tide(self, post, tide):
        notification = Notifications(user_id=self.id, event='1', post_id=post.id, stage=tide.stage)
        db.session.add(notification)

    def notify_wave(self, post, wave):
        notification = Notifications(user_id=self.id, event='2', post_id=post.id, stage=wave.stage, wave_id=wave.id)
        db.session.add(notification)

    def notify_reply(self, post, stage):
        notification = Notifications(user_id=self.id, event='3', post_id=post.id, stage=stage)
        db.session.add(notification)

    def new_notifications(self):
        new_notifications = Notifications.query.filter_by(user_id=self.id, seen=0).order_by(Notifications.date_posted.desc()).all()
        return len(new_notifications)

    #posting timeout checks, currently set to 1 second
    def timeout_post(self):
        last_post = Posts.query.filter_by(user_id=self.id).order_by(Posts.date_posted.desc()).first()
        if last_post:
            timedelta = datetime.utcnow() - last_post.date_posted
            return timedelta.seconds > 1
        else:
            return 1

    def timeout_comment(self):
        last_comment = Comments.query.filter_by(user_id=self.id).order_by(Comments.date_posted.desc()).first()
        if last_comment:
            timedelta = datetime.utcnow() - last_comment.date_posted
            return timedelta.seconds > 1
        else:
            return 1

    def timeout_reply(self):
        last_reply = Replies.query.filter_by(user_id=self.id).order_by(Replies.date_posted.desc()).first()
        if last_reply:
            timedelta = datetime.utcnow() - last_reply.date_posted
            return timedelta.seconds > 1
        else:
            return 1


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    tag = db.Column(db.String(10), unique=True, nullable=True)
    description = db.Column(db.String(250), nullable=False)
    posts = db.relationship('Posts', backref='tag', lazy=True, cascade="all, delete", passive_deletes=True)
    tides = db.relationship('Tides', backref='tag', lazy=True, cascade="all, delete", passive_deletes=True)
    comments = db.relationship('Comments', backref='tag', lazy=True, cascade="all, delete", passive_deletes=True)
    replies = db.relationship('Replies', backref='tag', lazy=True, cascade="all, delete", passive_deletes=True)


class Posts(db.Model):
    #msearch settings
    __tablename__ = 'posts'
    __searchable__ = ['title', 'description', 'content']
    __msearch_schema__ = {
        "title": TEXT(
            stored=True,
            analyzer=RegexTokenizer() | CaseSensitivizer(),
            sortable=False),
        "content": TEXT(
            stored=True,
            analyzer=RegexTokenizer(),
            sortable=False,
        )
    }

    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    link = db.Column(db.String(100), nullable=True)
    logo_file = db.Column(db.String(100), default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), nullable=False, default=1)
    tides = db.relationship('Tides', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    waves = db.relationship('Waves', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    comments = db.relationship('Comments', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    replies = db.relationship('Replies', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    subscribers = db.relationship('Subscriptions', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    notifications = db.relationship('Notifications', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    images = db.relationship('Images', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    links = db.relationship('Links', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)
    keywords = db.relationship('KeywordLinks', backref='post', lazy=True, cascade="all, delete", passive_deletes=True)

    # extraction methods used in jinja rendering and the serializer below
    def follownum(self): #subscribers
        followers = Subscriptions.query.filter_by(post_id=self.id).all()
        return len(followers)

    def commentnum(self): #combined number of comments and replies to all project stages
        comments = Comments.query.filter_by(post_id=self.id).all()
        replies = Replies.query.filter_by(post_id=self.id).all()
        return len(comments) + len(replies)

    def get_tag(self): 
        tag = Tags.query.filter_by(id=self.tag_id).first()
        return tag.tag

    #custom JSON serializer, this one is used for the homepage infinite scrolling feed
    @property
    def serialize(self):
        return {
            'title': self.title,
            'content': self.description,
            'comments': self.commentnum(),
            'subs': self.follownum(),
            'stage': self.stage,
            'logo': self.logo_file,
            'tag': self.get_tag(),
            'date_posted': moment.create(self.date_posted).fromNow()
        }


class Tides(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    banner_file = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    stage = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), nullable=False, default=1)


class Waves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    stage = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notifications = db.relationship('Notifications', backref='wave', lazy=True, cascade="all, delete", passive_deletes=True)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    stage = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    replies = db.relationship('Replies', backref='comments', lazy=True, cascade="all, delete", passive_deletes=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), nullable=False)


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    stage = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), nullable=False)


class Subscriptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    follows_since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    wave_id = db.Column(db.Integer, db.ForeignKey('waves.id', ondelete="CASCADE"), nullable=True)
    stage = db.Column(db.Integer, nullable=False, default=0)
    event = db.Column(db.String(15), nullable=False)
    content = db.Column(db.String(250), nullable=True)
    seen = db.Column(db.Integer, nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Notification on('{self.post.title}', '{self.user.username}')"


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Integer, nullable=False, default=0)
    filename = db.Column(db.String(100), default='default.jpg')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)



# the following three models were not introduced into the application yet
class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)


class Keywords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(50))
    posts = db.relationship('KeywordLinks', backref='keyword', lazy=True, cascade="all, delete", passive_deletes=True)


class KeywordLinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id', ondelete="CASCADE"), nullable=False)