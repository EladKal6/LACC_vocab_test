import pytest
from flask import Flask
from website.views import views
from website.auth import auth

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(views)
    app.register_blueprint(auth)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_status_page(client):
    response = client.get('/status')
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["version"] == "1.0"
    assert data["status"] == "OK"

def test_secret_page(client):
    response = client.get('/secret')
    assert response.status_code == 401
    assert response.is_json
    data = response.get_json()
    assert data["error"]["http_status"] == 401
    assert data["error"]["message"] == "You are not logged in"
    
