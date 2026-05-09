import pytest
import os
import tempfile
from flask import session
from app import app as flask_app
from database.db import init_db, get_db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    
    with flask_app.app_context():
        # Initialize tables
        init_db()
        yield flask_app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """A test client that is logged in and has specific test expenses."""
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        
        # Create user
        email = "test@example.com"
        password_hash = generate_password_hash("password")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Test User", email, password_hash)
        )
        user_id = cursor.lastrowid
        
        # Insert test expenses with specific past dates
        expenses = [
            (user_id, 100.00, "Food", "2023-01-01", "Old Food"),
            (user_id, 200.00, "Transport", "2023-02-01", "Mid Transport"),
            (user_id, 300.00, "Bills", "2023-03-01", "New Bills"),
        ]
        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
        conn.close()

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    return client


class TestProfileDateFilter:
    
    def test_auth_guard(self, client):
        """Test that unauthenticated requests to /profile redirect to /login."""
        response = client.get("/profile?date_from=2023-01-01&date_to=2023-12-31")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_unfiltered_profile_view(self, auth_client):
        """Test visiting /profile with no query parameters shows all data."""
        response = auth_client.get("/profile")
        assert response.status_code == 200
        
        # Check all transactions are shown
        html = response.data.decode()
        assert "Old Food" in html
        assert "Mid Transport" in html
        assert "New Bills" in html
        
        # Check total spent (100 + 200 + 300 = 600)
        assert "₹600.00" in html

    def test_valid_custom_date_range(self, auth_client):
        """Test filtering with a valid date range shows only matching expenses."""
        response = auth_client.get("/profile?date_from=2023-02-01&date_to=2023-03-01")
        assert response.status_code == 200
        
        html = response.data.decode()
        
        # Should not show the 2023-01-01 expense
        assert "Old Food" not in html
        
        # Should show the others
        assert "Mid Transport" in html
        assert "New Bills" in html
        
        # Check new total spent (200 + 300 = 500)
        assert "₹500.00" in html
        
        # Check the form values are populated (they should be present as values in the inputs)
        assert '2023-02-01' in html
        assert '2023-03-01' in html

    def test_reversed_dates_flash_error_and_fallback(self, auth_client):
        """Test that date_from > date_to flashes an error and falls back to unfiltered view."""
        response = auth_client.get("/profile?date_from=2023-03-01&date_to=2023-02-01", follow_redirects=True)
        assert response.status_code == 200
        
        html = response.data.decode()
        
        # Error message should be flashed
        assert "Start date must be before end date" in html
        
        # Should fall back to unfiltered view (all 3 transactions)
        assert "Old Food" in html
        assert "Mid Transport" in html
        assert "New Bills" in html
        assert "₹600.00" in html

    def test_malformed_dates_silent_fallback(self, auth_client):
        """Test that malformed date strings silently fall back to unfiltered view."""
        response = auth_client.get("/profile?date_from=invalid-date&date_to=also-invalid")
        assert response.status_code == 200
        
        html = response.data.decode()
        
        # No error flashed ideally, or at least it doesn't crash and shows full data
        assert "Start date must be before end date" not in html
        
        # Should fall back to unfiltered view
        assert "Old Food" in html
        assert "Mid Transport" in html
        assert "New Bills" in html
        assert "₹600.00" in html

    def test_empty_date_params_fallback(self, auth_client):
        """Test that empty string date params fall back to unfiltered view."""
        response = auth_client.get("/profile?date_from=&date_to=")
        assert response.status_code == 200
        
        html = response.data.decode()
        assert "₹600.00" in html
        assert "Old Food" in html

    def test_no_expenses_in_range(self, auth_client):
        """Test valid range that has no expenses displays correctly."""
        response = auth_client.get("/profile?date_from=2024-01-01&date_to=2024-12-31")
        assert response.status_code == 200
        
        html = response.data.decode()
        
        # Total spent should be ₹0.00
        assert "₹0.00" in html
        
        # Transaction count should be 0 - not strictly required to assert specific text,
        # but the transactions shouldn't appear
        assert "Old Food" not in html
        assert "Mid Transport" not in html
        assert "New Bills" not in html

    def test_presets_exist_in_template(self, auth_client):
        """Test that preset links are rendered in the HTML."""
        response = auth_client.get("/profile")
        assert response.status_code == 200
        
        html = response.data.decode()
        
        # Verify the preset buttons/links text is present
        assert "This Month" in html
        assert "Last 3 Months" in html
        assert "Last 6 Months" in html
        assert "All Time" in html
