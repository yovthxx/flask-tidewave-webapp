import os

def register_account(client): #register testing account
    return client.post('/register', data={'username': 'testing', 'email': 'testing@blog.com', 'password': 'testing', 'confirm_password': 'testing'}, follow_redirects=True)

def login(client): #logging method
    return client.post('/login', data={'email': 'testing@blog.com', 'password': 'testing'}, follow_redirects=True)

def login_admin(client): #logging method
    return client.post('/login', data={'email': 'admin@blog.com', 'password': 'admin'}, follow_redirects=True)

def logout(client): #logout method
    return client.get('/logout', follow_redirects=True)


#general routes
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_dirs(client):
    response = client.get('/dir')
    assert response.status_code == 200

#user tests
def test_registration(client):
    response = register_account(client)
    assert b'Your account has been created' in response.data

def test_login(client):
    response = login(client)
    assert b'You were logged in' in response.data

def test_login_fail(client):
    response = client.post('/login', data={'email': 'testing@blog.com', 'password': 'testingfail'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

def test_logout(client):
    response = logout(client)
    assert b'You were logged out' in response.data
     
def test_inbox(client):
    login(client)
    response = client.get('/inbox')
    assert b'Clear All' in response.data

def test_new_dir(client):
    login(client)
    response = client.post('/dir/new/test/test/test', follow_redirects=True)
    assert b'Projects' in response.data

def test_post_project(client):
    login(client)

    file = os.path.join(os.path.dirname(__file__), 'testing.png')
    data = {
        'logo': (open(file, 'rb'), file),
        'title':'TestTitle',
        'description':'TestDescription',
        'content':'TestContent'
    }
    response = client.post('/dir/test/project/new', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'TestTitle' in response.data

def test_post_tide(client):
    login(client)

    data = {
        'tide_title':'TestTide',
        'tide_content':'TestTideContent'
    }

    response = client.post('/dir/test/project/TestTitle/new_tide', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'TestTideContent' in response.data


def test_post_wave(client):
    login(client)

    data = {
        'wave_content': 'TestWave'
    }

    response = client.post('/dir/test/project/TestTitle/0/new_wave', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b'A wave posted!' in response.data

def test_post_tide_wave(client):
    login(client)

    data = {
        'wave_content': 'TestWaveTide'
    }

    response = client.post('/dir/test/project/TestTitle/0/new_wave', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b'A wave posted!' in response.data

def test_comment(client):
    login(client)

    data = {
        'comment_content': 'TestComment'
    }