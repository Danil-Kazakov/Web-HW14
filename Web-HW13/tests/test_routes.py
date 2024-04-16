import pytest
from unittest.mock import MagicMock, patch

import routes
from models import User
from auth import auth_service


def test_create_suer(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("routes.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['user']['email'] == user.get('email')
    assert 'id' in data['user']


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"