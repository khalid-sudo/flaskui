# tests/test_app.py

import pytest
from flask import Flask
from api.routes import api_blueprint
import os

@pytest.fixture
def client():
    # Explicitly set the template folder path
    app = Flask(__name__, template_folder='../templates')
    app.register_blueprint(api_blueprint, url_prefix="/")
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Anomaly detector" in response.data
