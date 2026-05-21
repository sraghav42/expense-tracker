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
        test_user_id = cursor.fetchone()["id"]

        cursor.execute("SELECT id FROM users WHERE email = 'other@example.com'")
        other_user_id = cursor.fetchone()["id"]

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


def test_edit_expense_auth_guard(app, auth_client_and_data):
    """Unauthenticated users should be redirected to login when trying to edit."""
    # Use a fresh, unauthenticated client
    client = app.test_client()
    expense_id = auth_client_and_data["test_expense_id"]

    # Test unauthenticated GET
    response = client.get(f"/expenses/{expense_id}/edit")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Test unauthenticated POST
    response = client.post(
        f"/expenses/{expense_id}/edit",
        data={
            "amount": 10.0,
            "category": "Food",
            "date": "2023-10-01",
            "description": "Update",
        },
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_edit_expense_get_happy_path(auth_client_and_data):
    """GET request to an existing expense owned by the user should prepopulate the form."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.get(f"/expenses/{expense_id}/edit")

    assert response.status_code == 200
    # The response data should include values of the expense
    assert b"50.0" in response.data or b"50" in response.data
    assert b"Test Food" in response.data
    assert b"2023-10-01" in response.data


def test_edit_expense_ownership_check(auth_client_and_data):
    """Users should not be able to access or edit someone else's expense."""
    client = auth_client_and_data["client"]
    other_expense_id = auth_client_and_data["other_expense_id"]

    # Try GET on another user's expense
    response = client.get(f"/expenses/{other_expense_id}/edit")
    assert response.status_code == 403

    # Try POST on another user's expense
    response = client.post(
        f"/expenses/{other_expense_id}/edit",
        data={
            "amount": 200.0,
            "category": "Food",
            "date": "2023-10-05",
            "description": "Hacked",
        },
    )
    assert response.status_code == 403


def test_edit_expense_not_found(auth_client):
    """Accessing an edit route for a non-existent expense returns 404."""
    response = auth_client.get("/expenses/9999/edit")
    assert response.status_code == 404


def test_edit_expense_post_happy_path(auth_client_and_data, app):
    """Valid POST updates the DB and redirects to profile."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(
        f"/expenses/{expense_id}/edit",
        data={
            "amount": 75.5,
            "category": "Shopping",
            "date": "2023-10-10",
            "description": "Updated Shoes",
        },
    )

    # Verify redirect
    assert response.status_code == 302
    assert "/profile" in response.headers["Location"]

    # Follow redirect to check success message
    follow_response = client.get("/profile")
    assert b"Expense updated successfully!" in follow_response.data

    # Verify DB update
    with app.app_context():
        from database.db import get_expense_by_id

        expense = get_expense_by_id(expense_id)
        assert expense["amount"] == 75.5
        assert expense["category"] == "Shopping"
        assert expense["date"] == "2023-10-10"
        assert expense["description"] == "Updated Shoes"


@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "category": "Food",
            "date": "2023-10-10",
            "description": "Desc",
        },  # missing amount
        {
            "amount": "",
            "category": "Food",
            "date": "2023-10-10",
            "description": "Desc",
        },  # empty amount
        {
            "amount": 50,
            "category": "",
            "date": "2023-10-10",
            "description": "Desc",
        },  # empty category
        {
            "amount": 50,
            "category": "Food",
            "date": "",
            "description": "Desc",
        },  # empty date
        {
            "amount": 50,
            "category": "Food",
            "date": "2023-10-10",
            "description": "",
        },  # empty description
    ],
)
def test_edit_expense_missing_fields(auth_client_and_data, app, invalid_data):
    """Missing or empty fields should trigger a flash error and not update the DB."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(f"/expenses/{expense_id}/edit", data=invalid_data)

    assert response.status_code == 200
    assert b"All fields are required." in response.data

    # Ensure DB value is unchanged
    with app.app_context():
        from database.db import get_expense_by_id

        expense = get_expense_by_id(expense_id)
        assert expense["amount"] == 50.0  # Still original value


@pytest.mark.parametrize(
    "invalid_amount, expected_message",
    [
        ("abc", b"Invalid amount."),
        ("-10", b"Amount must be greater than zero."),
        ("0", b"Amount must be greater than zero."),
    ],
)
def test_edit_expense_invalid_amount(
    auth_client_and_data, app, invalid_amount, expected_message
):
    """Invalid amount types/values should trigger an error and not update the DB."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(
        f"/expenses/{expense_id}/edit",
        data={
            "amount": invalid_amount,
            "category": "Food",
            "date": "2023-10-10",
            "description": "Desc",
        },
    )

    assert response.status_code == 200
    assert expected_message in response.data

    # Ensure DB value is unchanged
    with app.app_context():
        from database.db import get_expense_by_id

        expense = get_expense_by_id(expense_id)
        assert expense["amount"] == 50.0


def test_edit_expense_invalid_category(auth_client_and_data, app):
    """A category not in the allowed list should trigger an error."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.post(
        f"/expenses/{expense_id}/edit",
        data={
            "amount": 50,
            "category": "NotARealCategory",
            "date": "2023-10-10",
            "description": "Desc",
        },
    )

    assert response.status_code == 200
    assert b"Invalid category selected." in response.data

    # Ensure DB value is unchanged
    with app.app_context():
        from database.db import get_expense_by_id

        expense = get_expense_by_id(expense_id)
        assert expense["category"] == "Food"


def test_profile_displays_edit_link(auth_client_and_data):
    """The profile page should display a link to edit existing transactions."""
    client = auth_client_and_data["client"]
    expense_id = auth_client_and_data["test_expense_id"]

    response = client.get("/profile")
    assert response.status_code == 200

    # Since we can't assume exact HTML structure, check for the edit route path
    expected_url = f"/expenses/{expense_id}/edit".encode()
    assert expected_url in response.data, "Expected edit link on profile page"
