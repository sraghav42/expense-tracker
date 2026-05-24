import tempfile
import pytest
from app import app as flask_app
from database.db import init_db, get_db


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "DATABASE": tempfile.mkstemp()[1],
            "SECRET_KEY": "test-secret",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with flask_app.app_context():
        init_db()
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client_and_data(client, app):
    """Creates two users, logs in as the first, and inserts an expense for each."""
    client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )

    client.post(
        "/register",
        data={
            "name": "Other User",
            "email": "other@example.com",
            "password": "password",
            "confirm_password": "password",
        },
    )

    # Login as test user
    client.post("/login", data={"email": "test@example.com", "password": "password"})

    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = 'test@example.com'")
        test_user = cursor.fetchone()
        test_user_id = test_user["id"] if test_user else 1

        cursor.execute("SELECT id FROM users WHERE email = 'other@example.com'")
        other_user = cursor.fetchone()
        other_user_id = other_user["id"] if other_user else 2

        # Insert expense for test user
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (test_user_id, 50.0, "Food", "2023-10-01", "Test Food"),
        )
        expense_1_id = cursor.lastrowid

        # Insert expense for other user
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (other_user_id, 100.0, "Transport", "2023-10-02", "Other Transport"),
        )
        expense_2_id = cursor.lastrowid
        conn.commit()

    return {
        "client": client,
        "test_user_id": test_user_id,
        "other_user_id": other_user_id,
        "test_expense_id": expense_1_id,
        "other_expense_id": expense_2_id,
    }


@pytest.fixture
def auth_client(auth_client_and_data):
    return auth_client_and_data["client"]


def test_delete_expense_auth_guard_get(app, auth_client_and_data):
    """Unauthenticated GET requests to delete route should redirect to login."""
    client = app.test_client()
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.get(f"/expenses/{expense_id}/delete")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_expense_auth_guard_post(app, auth_client_and_data):
    """Unauthenticated POST requests to delete route should redirect to login."""
    client = app.test_client()
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(f"/expenses/{expense_id}/delete")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_expense_get_confirmation_page(auth_client_and_data):
    """GET requests to delete route by the owner should return the confirmation page."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.get(f"/expenses/{expense_id}/delete")
    assert response.status_code == 200
    # Allow various text that indicates a confirmation page or expense values
    assert (
        b"Food" in response.data
        or b"Test Food" in response.data
        or b"Delete" in response.data
    )


def test_delete_expense_missing_get(auth_client_and_data):
    """GET requests to a non-existent expense should return 404."""
    client = auth_client_and_data["client"]
    response = client.get("/expenses/9999/delete")
    assert response.status_code == 404


def test_delete_expense_missing_post(auth_client_and_data):
    """POST requests to a non-existent expense should return 404."""
    client = auth_client_and_data["client"]
    response = client.post("/expenses/9999/delete")
    assert response.status_code == 404


def test_delete_expense_unauthorized_get(auth_client_and_data):
    """GET requests to another user's expense should return 403."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["other_expense_id"]

    response = client.get(f"/expenses/{expense_id}/delete")
    assert response.status_code == 403


def test_delete_expense_unauthorized_post(auth_client_and_data):
    """POST requests to another user's expense should return 403."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["other_expense_id"]

    response = client.post(f"/expenses/{expense_id}/delete")
    assert response.status_code == 403


def test_delete_expense_success_post(app, auth_client_and_data):
    """POST requests by the owner should delete the expense, flash success, and redirect to profile."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(f"/expenses/{expense_id}/delete")
    assert response.status_code == 302
    assert "/profile" in response.headers["Location"]

    # Verify DB side effect
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
        result = cursor.fetchone()
        assert result is None, "Expense should be deleted from the database"

        # Ensure the other expense is untouched
        other_expense_id = auth_client_and_data["other_expense_id"]
        cursor.execute("SELECT id FROM expenses WHERE id = ?", (other_expense_id,))
        result = cursor.fetchone()
        assert result is not None, "Other expense should remain in the database"
        conn.close()
