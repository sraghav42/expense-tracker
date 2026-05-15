import pytest
import os
import tempfile
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    # Use a temporary file for the database to avoid cross-connection persistence issues
    # that can happen with ':memory:' when connections are opened and closed per request.
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    
    with flask_app.app_context():
        init_db()
        yield flask_app
        
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'testpass'
    })
    return client

class TestAddExpense:
    
    def test_add_expense_auth_guard(self, client):
        """Unauthenticated requests to protected routes return 302 to /login"""
        # GET request
        response_get = client.get('/expenses/add')
        assert response_get.status_code == 302, "Expected redirect to login"
        assert '/login' in response_get.headers['Location'], "Expected redirect to login"
        
        # POST request
        response_post = client.post('/expenses/add', data={
            'amount': '100',
            'category': 'Food',
            'date': '2023-10-01',
            'description': 'Lunch'
        })
        assert response_post.status_code == 302, "Expected redirect to login"
        assert '/login' in response_post.headers['Location'], "Expected redirect to login"

    def test_add_expense_get_form(self, auth_client):
        """Logged-in users should be able to view the add expense form"""
        response = auth_client.get('/expenses/add')
        assert response.status_code == 200, "Expected 200 OK for add expense page"
        # Since we use url_for in the template, checking for form presence
        assert b'<form' in response.data, "Expected a form in the template"
        
    def test_add_expense_post_success(self, auth_client, app):
        """Submitting a valid expense saves to DB and redirects to profile"""
        form_data = {
            'amount': '45.50',
            'category': 'Food',
            'date': '2023-10-01',
            'description': 'Grocery shopping'
        }
        
        response = auth_client.post('/expenses/add', data=form_data)
        
        # Check HTTP semantics
        assert response.status_code == 302, "Expected redirect on success"
        assert '/profile' in response.headers['Location'], "Expected redirect to profile page"
        
        # Follow redirect to check for success flash message
        profile_response = auth_client.get('/profile')
        assert b'Expense added successfully!' in profile_response.data, "Expected success flash message"
        
        # Check DB side effects
        with app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE description = 'Grocery shopping'")
            expense = cursor.fetchone()
            conn.close()
            
            assert expense is not None, "Expense was not saved to database"
            assert expense['amount'] == 45.50, "Saved amount does not match"
            assert expense['category'] == 'Food', "Saved category does not match"
            assert expense['date'] == '2023-10-01', "Saved date does not match"
            
    @pytest.mark.parametrize('missing_field,form_data', [
        ('amount', {'category': 'Food', 'date': '2023-10-01', 'description': 'Lunch'}),
        ('category', {'amount': '100', 'date': '2023-10-01', 'description': 'Lunch'}),
        ('date', {'amount': '100', 'category': 'Food', 'description': 'Lunch'}),
        ('description', {'amount': '100', 'category': 'Food', 'date': '2023-10-01'})
    ])
    def test_add_expense_missing_fields(self, auth_client, missing_field, form_data):
        """Form validation prevents submission of empty fields"""
        response = auth_client.post('/expenses/add', data=form_data)
        
        # Should stay on the same page and render an error
        assert response.status_code == 200, f"Expected 200 OK when {missing_field} is missing"
        assert b'All fields are required.' in response.data, f"Expected flash error when {missing_field} is missing"

    def test_add_expense_empty_string_fields(self, auth_client):
        """Form validation prevents submission of empty string fields"""
        form_data = {
            'amount': '100',
            'category': 'Food',
            'date': '2023-10-01',
            'description': '   ' # Effectively empty, or we can use empty string
        }
        form_data['description'] = ''
        
        response = auth_client.post('/expenses/add', data=form_data)
        assert response.status_code == 200, "Expected 200 OK when description is empty string"
        assert b'All fields are required.' in response.data, "Expected flash error for empty description"
        
    def test_add_expense_invalid_amount(self, auth_client):
        """Form validation requires amount to be a valid float"""
        form_data = {
            'amount': 'not_a_number',
            'category': 'Food',
            'date': '2023-10-01',
            'description': 'Lunch'
        }
        
        response = auth_client.post('/expenses/add', data=form_data)
        
        # Should stay on the same page and render an error
        assert response.status_code == 200, "Expected 200 OK when amount is invalid"
        assert b'Invalid amount.' in response.data, "Expected 'Invalid amount.' flash error"

    def test_add_expense_invalid_category(self, auth_client):
        """Form validation requires category to be one of the allowed options"""
        form_data = {
            'amount': '100',
            'category': 'NotARealCategory',
            'date': '2023-10-01',
            'description': 'Lunch'
        }
        
        response = auth_client.post('/expenses/add', data=form_data)
        
        assert response.status_code == 200, "Expected 200 OK when category is invalid"
        assert b'Invalid category selected.' in response.data, "Expected 'Invalid category selected.' flash error"

    @pytest.mark.parametrize('invalid_amount', ['0', '-50.5'])
    def test_add_expense_non_positive_amount(self, auth_client, invalid_amount):
        """Form validation requires amount to be strictly greater than zero"""
        form_data = {
            'amount': invalid_amount,
            'category': 'Food',
            'date': '2023-10-01',
            'description': 'Lunch'
        }
        
        response = auth_client.post('/expenses/add', data=form_data)
        
        assert response.status_code == 200, f"Expected 200 OK when amount is {invalid_amount}"
        assert b'Amount must be greater than zero.' in response.data, "Expected 'Amount must be greater than zero.' flash error"

    def test_add_expense_retains_form_data_on_error(self, auth_client):
        """Form data is re-populated in the HTML when a validation error occurs"""
        form_data = {
            'amount': '-10', # Invalid amount to trigger error
            'category': 'Food',
            'date': '2023-10-01',
            'description': 'Test Description Data Retention'
        }
        
        response = auth_client.post('/expenses/add', data=form_data)
        
        assert response.status_code == 200, "Expected 200 OK when amount is negative"
        
        # Check that the form fields contain the submitted data
        response_text = response.data.decode('utf-8')
        assert '-10' in response_text, "Expected amount to be retained in form"
        assert 'Test Description Data Retention' in response_text, "Expected description to be retained in form"
        assert '2023-10-01' in response_text, "Expected date to be retained in form"
