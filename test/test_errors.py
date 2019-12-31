"""Unit testing for error views."""

from flask import url_for

from test.setup_tests import SetupTest, USR

# Global test variables
FAKE_ROUTE = "/fake/test/route"
ERR_404_STR = b"File Not Found"
ERR_405_STR = b"Method Not Allowed"
ERR_CSRF = b"Your request could not be processed"
ERR_500 = b"An unexpected error has occurred"


class TestErrors(SetupTest):
    def test_err_404(self):
        """Ensure 404 errors are handled properly."""

        resp = self.client.get(FAKE_ROUTE)
        assert resp.status_code == 404
        assert ERR_404_STR in resp.data

    def test_err_405(self):
        """Ensure 405 errors are handled properly."""

        resp = self.client.get(url_for("api.message"))
        assert resp.status_code == 405
        assert ERR_405_STR in resp.data

    def test_err_csrf(self):
        """Ensure CSRF errors are handled properly."""

        self.app.config["WTF_CSRF_ENABLED"] = True
        data = {"email": USR, "password": "password", "confirm": "password"}
        resp = self.client.post(
            url_for("user.login"), data=data, follow_redirects=True
        )
        assert resp.status_code == 400
        assert ERR_CSRF in resp.data
