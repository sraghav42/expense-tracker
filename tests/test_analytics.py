import pytest
from app import app as flask_app
from database.db import init_db, seed_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        seed_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1  # User ID 1 is created by seed_db
    return client

def test_analytics_requires_auth(client):
    """Test that an unauthenticated user is redirected to the login page."""
    response = client.get('/analytics')
    
    assert response.status_code == 302, "Expected redirect for unauthenticated user"
    assert '/login' in response.headers.get('Location', ''), "Expected redirect to point to /login"

def test_analytics_returns_200(auth_client):
    """Test that an authenticated user can access the analytics page."""
    response = auth_client.get('/analytics')
    
    assert response.status_code == 200, "Expected 200 OK for authenticated user"

def test_analytics_content(auth_client):
    """Test that the analytics page contains the expected placeholders."""
    response = auth_client.get('/analytics')
    html = response.data.decode('utf-8')
    
    assert 'Analytics' in html, "Expected 'Analytics' to be present in the page content"
    assert 'Coming Soon' in html, "Expected 'Coming Soon' message to be present"
    assert 'Deep Insights' in html, "Expected card header to be present"

def test_navbar_includes_analytics_when_logged_in(auth_client):
    """Test that the 'Analytics' link is present in the navigation bar when logged in."""
    # Check another authenticated page like /profile to verify global navbar
    response = auth_client.get('/profile')
    html = response.data.decode('utf-8')
    
    assert 'href="/analytics"' in html, "Expected Analytics link in navbar"
    assert 'Analytics' in html, "Expected 'Analytics' text in navbar"
