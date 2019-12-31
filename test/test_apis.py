"""Unit testing for Flask APIs."""

import json

from flask import url_for

from app.models.db import User
from app.utils.auth import generate_jwt
from test.setup_tests import SetupTest, USR

HEALTH = {"status": "online"}


class TestChangePassword(SetupTest):
    """Tests the change password API in app.views.api.py"""

    def test_change_password_no_token(self):
        """Ensure a token is required to access this API."""
        resp = self.client.put(
            url_for("api.change_password"), data={"password": "new_password"}
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_change_password_invalid_token(self):
        """Ensure a valid token is required to access this API."""
        resp = self.client.put(
            url_for("api.change_password"),
            data={"password": "new_password"},
            headers={"Authorization": "Bearer InvalidToken"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_change_password_invalid(self):
        """Ensure invalid change password information is rejected."""
        data_sets = [{"pass": "password"}, {}]
        user = User.query.filter(User.email == USR).first()
        token = generate_jwt(user.email, user.get_roles())
        for data in data_sets:
            resp = self.client.put(
                url_for("api.change_password"),
                data=json.dumps(data),
                content_type="application/json",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code in [400, 401]

    def test_change_password_valid(self):
        """Ensure valid change password information is accepted."""
        user = User.query.filter(User.email == USR).first()
        token = generate_jwt(user.email, user.get_roles())
        resp = self.client.put(
            url_for("api.change_password"),
            data=json.dumps({"password": "new_password"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 200
        assert data["status"] == "success"


class TestDeleteAccount(SetupTest):
    """Tests the delete account API in app.views.api.py"""

    def test_delete_account_no_token(self):
        """Ensure a token is required to access this API."""
        resp = self.client.delete(url_for("api.delete_account"))
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_delete_account_invalid_token(self):
        """Ensure a valid token is required to access this API."""
        resp = self.client.delete(
            url_for("api.delete_account"),
            headers={"Authorization": "Bearer InvalidToken"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_delete_account_valid(self):
        """Ensure valid delete account information is accepted."""
        user = User.query.filter(User.email == USR).first()
        token = generate_jwt(user.email, user.get_roles())
        resp = self.client.delete(
            url_for("api.delete_account"),
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 200
        assert data["status"] == "success"


class TestHealth(SetupTest):
    """Tests the health API in app.views.api.py"""

    def test_basic(self):
        """Ensure the view returns the proper JSON response."""
        resp = self.client.get(url_for("api.health"))
        data = json.loads(resp.get_data())
        assert resp.status_code == 200
        assert data == HEALTH


class TestMessage(SetupTest):
    """Tests the message API in app.views.api.py"""

    def test_message_no_token(self):
        """Ensure a token is required to access this API."""
        resp = self.client.post(
            url_for("api.message"),
            data={
                "category": "Other",
                "first": "Test",
                "last": "Test",
                "message": "Testing",
            },
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_message_invalid_token(self):
        """Ensure a valid token is required to access this API."""
        resp = self.client.post(
            url_for("api.message"),
            data={
                "category": "Other",
                "first": "Test",
                "last": "Test",
                "message": "Testing",
            },
            headers={"Authorization": "Bearer InvalidToken"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 401
        assert data["status"] == "failure"

    def test_message_invalid(self):
        """Ensure invalid message information is rejected."""
        data_sets = [
            {"last": "Test", "message": "Testing"},
            {"first": "Test", "message": "Testing"},
            {"first": "Test", "last": "Test"},
        ]
        user = User.query.filter(User.email == USR).first()
        token = generate_jwt(user.email, user.get_roles())
        for data in data_sets:
            resp = self.client.post(
                url_for("api.message"),
                data=json.dumps(data),
                content_type="application/json",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code in [400, 401]

    def test_message_valid(self):
        """Ensure valid message information is accepted."""
        user = User.query.filter(User.email == USR).first()
        token = generate_jwt(user.email, user.get_roles())
        resp = self.client.post(
            url_for("api.message"),
            data=json.dumps(
                {
                    "category": "Other",
                    "first": "Test",
                    "last": "Test",
                    "message": "Testing",
                },
            ),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 200
        assert data["status"] == "success"


class TestToken(SetupTest):
    """Tests the token API in app.views.api.py"""

    def test_token_invalid(self):
        """Ensure invalid token information is rejected."""
        data_sets = [
            {"email": USR, "password": "pass"},
            {"email": USR},
            {"password": "password"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("api.token"),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert resp.status_code in [400, 401]

    def test_token_valid(self):
        """Ensure valid token information is accepted."""
        resp = self.client.post(
            url_for("api.token"),
            data=json.dumps({"email": USR, "password": "password"}),
            content_type="application/json",
        )
        data = json.loads(resp.get_data())
        assert resp.status_code == 200
        assert data["status"] == "success"
        assert data["token"] is not None
