import pytest
import os

from tidewave import create_app
from tidewave import db

dirname = os.path.dirname(__file__)


@pytest.fixture(scope='session')
def app(request):

    app = create_app()

    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testwave.db'
    app.config['TESTING'] = True

    #app context
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    def teardown():
        db.drop_all()
        ctx.pop()
        
    
    request.addfinalizer(teardown)
    return app