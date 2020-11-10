from flask import render_template, request, Blueprint, jsonify, make_response, session
from flask_login import current_user, login_required
from tidewave.models import Posts, Tags
from tidewave import db


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home(): #posts on home page are loaded via JQuery(InfiniteScroll scrypt), loading route is available in the posts module
    dirs = Tags.query.limit(10)
    return render_template('home.html', dirs=dirs)
