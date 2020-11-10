from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from tidewave.config import Config
from flask_msearch import Search
from flask_moment import Moment

db = SQLAlchemy()
search = Search()
bcrypt = Bcrypt()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    search.init_app(app)

    from tidewave.users.routes import users
    from tidewave.posts.routes import posts
    from tidewave.main.routes import main
    from tidewave.errors.handlers import errors
    from tidewave.tags.routes import tags
    from tidewave.tides.routes import tides
    from tidewave.comments.routes import comments
    from tidewave.waves.routes import waves
    from tidewave.services.routes import services

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(tags)
    app.register_blueprint(tides)
    app.register_blueprint(comments)
    app.register_blueprint(waves)
    app.register_blueprint(services)

    with app.app_context():
        db.create_all()

    return app
