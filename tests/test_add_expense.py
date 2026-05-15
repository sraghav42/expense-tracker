# tests/test_add_expense.py
import pytest
import tempfile
import os
from app import app as flask_app
from database.db import init_db, seed_db, get_recent_transactions, get_user_stats

@pytest.fixture
def app():
    """Provides a fresh Flask app instance with an isolated temporary database."""
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    
    with flask_app.app_context():
        init_db()
        seed_db()
        yield flask_app
        
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A standard test client for unauthenticated requests."""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in as the seeded user (ID 1)."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    return client

class TestAddExpense:

    def test_add_expense_unauthenticated_get(self, client):
        """GET /expenses/add should redirect to login if not authenticated."""
        response = client.get("/expenses/add")
        
        assert response.status_code == 302
        assert "/login" in response.headers["Location"], "Expected redirect to login page"

    def test_add_expense_unauthenticated_post(self, client):
        """POST /expenses/add should redirect to login if not authenticated."""
        response = client.post("/expenses/add", data={
            "amount": "10.00",
            "category": "Food",
            "date": "2026-05-10",
            "description": "Lunch"
        })
        
        assert response.status_code == 302
        assert "/login" in response.headers["Location"], "Expected redirect to login page"

    def test_add_expense_get_authenticated(self, auth_client):
        """GET /expenses/add should render the add expense form for authenticated users."""
        response = auth_client.get("/expenses/add")
        
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert 'name="amount"' in html, "Missing amount input field"
        assert 'name="category"' in html, "Missing category input field"
        assert 'name="date"' in html, "Missing date input field"
        assert 'name="description"' in html, "Missing description input field"

    def test_add_expense_post_success(self, auth_client, app):
        """POST /expenses/add with valid data should create expense, update stats, and redirect."""
        # Capture initial stats before submission
        with app.app_context():
            initial_stats = get_user_stats(1)
            initial_count = initial_stats["transaction_count"]
            initial_total = initial_stats["total_spent"]
            
        response = auth_client.post("/expenses/add", data={
            "amount": "50.25",
            "category": "Entertainment",
            "date": "2026-05-01",
            "description": "Movie ticket"
        })
        
        # Verify redirect to profile
        assert response.status_code == 302
        assert "/profile" in response.headers["Location"], "Expected redirect to profile on success"
        
        # Follow the redirect to verify the flash message
        profile_response = auth_client.get("/profile")
        assert b"Expense added successfully!" in profile_response.data
        
        # Verify DB side effects (transaction created and stats updated)
        with app.app_context():
            # Check transaction list
            transactions = get_recent_transactions(1)
            movie_transaction = next((t for t in transactions if t["description"] == "Movie ticket"), None)
            
            assert movie_transaction is not None, "Expense was not saved to the database"
            assert movie_transaction["amount"] == 50.25
            assert movie_transaction["category"] == "Entertainment"
            assert movie_transaction["date"] == "2026-05-01"
            
            # Check updated stats
            new_stats = get_user_stats(1)
            assert new_stats["transaction_count"] == initial_count + 1, "Transaction count did not increment"
            assert new_stats["total_spent"] == initial_total + 50.25, "Total spent did not update correctly"

    @pytest.mark.parametrize("missing_field", ["amount", "category", "date", "description"])
    def test_add_expense_post_missing_fields(self, auth_client, missing_field):
        """POST /expenses/add with any missing field should show an error and re-render the form."""
        data = {
            "amount": "15.00",
            "category": "Transport",
            "date": "2026-05-02",
            "description": "Bus fare"
        }
        # Remove the specific required field for this test iteration
        data[missing_field] = ""
        
        response = auth_client.post("/expenses/add", data=data)
        
        # Should stay on the same page with a 200 OK
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "All fields are required." in html, f"Missing flash error for empty {missing_field}"

    def test_add_expense_post_invalid_amount(self, auth_client):
        """POST /expenses/add with a non-numeric amount should show an error."""
        # Use a string that float() cannot convert
        response = auth_client.post("/expenses/add", data={
            "amount": "not-a-number",
            "category": "Food",
            "date": "2026-05-03",
            "description": "Dinner"
        })
        
        # Should stay on the same page with a 200 OK
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Invalid amount." in html, "Missing flash error for invalid amount"
