"""Unit testing for Flask views."""

from flask import url_for

from app.utils.auth import serialize_pw_token
from test.setup_tests import force_anon_user, force_auth_user, SetupTest, USR

# Global testing parameters
CONTACT_SUCCESS = b"Message submitted successfully"
DELETE = b"Delete Account"
DELETE_SUCCESS = b", has been removed"
INDEX = b'<h2 id="about"'
INVALID_REQUEST = b"Your request is not valid"
LOGIN = b">Please Sign In</h3>"
LOGIN_SUCCESS = b"Login Successful"
NO_LONGER_VALID = b"Your request is no longer valid"
RECOVER = b"Account Recovery"
RECOVER_SUCCESS = b"Account recovery email sent successfully"
REGISTER = b"Register Account"
REGISTER_SUCCESS = b"Account registration successful"
RESET = b"Reset Password"
RESET_SUCCESS = b"Your password has been updated successfully"
UNAUTHORIZED = b">You are not authorized to access the URL requested</p>"


class TestAdmin(SetupTest):
    """Tests the views in app.views.admin.py"""

    def test_adm_auth(self):
        """Ensure admin users can reach the admin page."""
        force_auth_user(app=self.app, admin=True)
        resp = self.client.get(url_for("admin.adm"), follow_redirects=True)
        assert resp.status_code == 200
        assert UNAUTHORIZED not in resp.data

    def test_no_auth(self):
        """Ensure anonymous users cannot reach the admin page."""
        force_anon_user(app=self.app)
        resp = self.client.get(url_for("admin.adm"), follow_redirects=True)
        assert resp.status_code == 401
        assert UNAUTHORIZED in resp.data

    def test_usr_auth(self):
        """Ensure non admin users cannot reach the admin page."""
        force_auth_user(app=self.app)
        resp = self.client.get(url_for("admin.adm"), follow_redirects=True)
        assert resp.status_code == 401
        assert UNAUTHORIZED in resp.data


class TestDeleteUser(SetupTest):
    """Tests the delete view in app.views.user.py"""

    def test_no_auth(self):
        """Ensure unauthorized users cannot reach the delete page."""
        force_anon_user(app=self.app)
        resp = self.client.get(url_for("user.delete"), follow_redirects=True)
        assert resp.status_code == 200
        assert LOGIN in resp.data

    def test_delete_invalid(self):
        """Ensure invalid delete form information is rejected."""
        force_auth_user(app=self.app)
        data_sets = [
            {"pw": "password", "confirm": "pass"},
            {"confirm": "pass"},
            {"pw": "password"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("user.delete"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert DELETE in resp.data
            assert DELETE_SUCCESS not in resp.data

    def test_delete_valid(self):
        """Ensure valid delete form information is accepted."""
        force_auth_user(app=self.app)
        data = {"pw": "password", "confirm": "password"}
        resp = self.client.post(
            url_for("user.delete"), data=data, follow_redirects=True
        )
        assert resp.status_code == 200
        assert INDEX in resp.data
        assert DELETE_SUCCESS in resp.data


class TestIndex(SetupTest):
    """Tests the views in app.views.base.py"""

    def test_basic(self):
        """Ensure the index view reaches the proper page."""
        resp = self.client.get(url_for("base.index"))
        assert resp.status_code == 200
        assert INDEX in resp.data

    def test_contact_valid(self):
        """Ensure invalid contact form information is rejected."""
        data_sets = [
            {
                "first": "Test",
                "last": "Test",
                "email": "Test.Test@Test.com",
                "message": "Testing",
            },
            {"first": "Test", "last": "Test", "message": "Testing"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("base.index"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert INDEX in resp.data
            assert CONTACT_SUCCESS in resp.data

    def test_contact_invalid(self):
        """Ensure valid contact form information is accepted."""
        data_sets = [
            {
                "last": "Test",
                "email": "Test.Test@Test.com",
                "message": "Testing",
            },
            {"first": "Test", "message": "Testing"},
            {"first": "Test", "last": "Test", "email": "Test.Test@Test.com"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("base.index"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert INDEX in resp.data
            assert CONTACT_SUCCESS not in resp.data


class TestLoginUser(SetupTest):
    """Tests the login view in app.views.user.py"""

    def test_auth_valid(self):
        """Ensure valid login form information is accepted."""
        data = {"email": USR, "pw": "password"}
        resp = self.client.post(
            url_for("user.login"), data=data, follow_redirects=True
        )
        assert resp.status_code == 200
        assert INDEX in resp.data
        assert LOGIN_SUCCESS in resp.data

    def test_auth_invalid(self):
        """Ensure invalid login form information is rejected."""
        data_sets = [
            {"email": USR, "pw": "pass"},
            {"email": "fake@fake.com", "pw": "password"},
            {"email": USR},
            {"pw": "password"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("user.login"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert LOGIN in resp.data
            assert LOGIN_SUCCESS not in resp.data


class TestLogoutUser(SetupTest):
    """Tests the logout view in app.views.user.py"""

    def test_auth(self):
        """Ensure authenticated users can logout."""
        force_auth_user(app=self.app)
        resp = self.client.get(url_for("user.logout"), follow_redirects=True)
        assert resp.status_code == 200
        assert INDEX in resp.data

    def test_no_auth(self):
        """Ensure unauthenticated users are directed to login."""
        force_anon_user(app=self.app)
        resp = self.client.get(url_for("user.logout"), follow_redirects=True)
        assert resp.status_code == 200
        assert LOGIN in resp.data


class TestRecoverUser(SetupTest):
    """Tests the recover view in app.views.user.py"""

    def test_recover_valid(self):
        """Ensure valid recover form information is accepted."""
        data = {"email": USR, "confirm": USR}
        resp = self.client.post(
            url_for("user.recover"), data=data, follow_redirects=True
        )
        assert resp.status_code == 200
        assert LOGIN in resp.data
        assert RECOVER_SUCCESS in resp.data

    def test_recover_invalid(self):
        """Ensure invalid recover form information is rejected."""
        data_sets = [
            {"email": USR, "confirm": ""},
            {"email": "fake@fake.com", "confirm": USR},
            {"email": USR},
            {"confirm": USR},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("user.recover"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert RECOVER in resp.data
            assert RECOVER_SUCCESS not in resp.data


class TestRegisterUser(SetupTest):
    """Tests the register view in app.views.user.py"""

    def test_register_valid(self):
        """Ensure valid register form information is accepted."""
        data = {
            "email": "test@test.com",
            "pw": "testing123",
            "confirm": "testing123",
        }
        resp = self.client.post(
            url_for("user.register"), data=data, follow_redirects=True
        )
        assert resp.status_code == 200
        assert LOGIN in resp.data
        assert REGISTER_SUCCESS in resp.data

    def test_register_invalid(self):
        """Ensure invalid register form information is rejected."""
        data_sets = [
            {"email": "test@test.com", "pw": "password", "confirm": "pass"},
            {"email": "test@test.com", "confirm": ""},
            {"pw": "password", "confirm": "password"},
            {"email": "test@test.com", "pw": "password"},
        ]

        for data in data_sets:
            resp = self.client.post(
                url_for("user.register"), data=data, follow_redirects=True
            )
            assert resp.status_code == 200
            assert REGISTER in resp.data
            assert REGISTER_SUCCESS not in resp.data


class TestResetUser(SetupTest):
    """Tests the reset view in app.views.user.py"""

    def test_no_token(self):
        """Ensure requests with no token are rejected."""
        resp = self.client.get(url_for("user.reset"), follow_redirects=True)
        assert resp.status_code == 200
        assert INDEX in resp.data
        assert INVALID_REQUEST in resp.data

    def test_invalid_token(self):
        """Ensure requests with invalid tokens are rejected."""
        route = f"{url_for('user.reset')}?token=invalid_token"
        resp = self.client.get(route, follow_redirects=True)
        assert resp.status_code == 200
        assert RECOVER in resp.data
        assert NO_LONGER_VALID in resp.data

    def test_reset_valid(self):
        """Ensure valid reset form information is accepted."""

        with self.app.app_context():
            valid_token = serialize_pw_token(USR)
        route = f"{url_for('user.reset')}?token={valid_token}"
        data = {"pw": "new_password", "confirm": "new_password"}
        resp = self.client.post(route, data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert LOGIN in resp.data
        assert RESET_SUCCESS in resp.data

    def test_reset_invalid(self):
        """Ensure invalid reset form information is rejected."""

        with self.app.app_context():
            valid_token = serialize_pw_token(USR)
        route = f"{url_for('user.reset')}?token={valid_token}"
        data_sets = [
            {"pw": "new_password"},
            {"confirm": "new_password"},
            {"pw": "no_match", "confirm": "noo_match"},
        ]
        for data in data_sets:
            resp = self.client.post(route, data=data, follow_redirects=True)
            assert resp.status_code == 200
            assert RESET in resp.data
            assert RESET_SUCCESS not in resp.data
