import pytest
from app import app
from database.db import get_db, init_db, seed_db, get_recent_transactions, get_user_stats, get_category_breakdown

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
            seed_db()
        yield client

def test_get_recent_transactions():
    with app.app_context():
        # Demo user ID is likely 1
        transactions = get_recent_transactions(1)
        assert len(transactions) > 0
        assert "amount" in transactions[0].keys()
        assert "date" in transactions[0].keys()
        
        # Check ordering (date DESC, created_at DESC)
        # Sample seed data has dates 2026-04-01 to 2026-04-08
        # So the first one should be 2026-04-08
        assert transactions[0]["date"] == "2026-04-08"

def test_profile_route_data(client):
    # Log in as demo user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    response = client.get('/profile')
    assert response.status_code == 200
    
    # We can't easily check the rendered template content here without more effort,
    # but we've verified the logic that feeds it.
    # If we want to check the content, we'd look for the formatted amounts.
    html = response.data.decode('utf-8')
    assert "$45.50" in html # From seed data
    assert "$22.00" in html # From seed data

def test_get_user_stats():
    with app.app_context():
        # Demo user ID is 1
        stats = get_user_stats(1)
        
        # Seed data has 8 expenses:
        # 45.50, 15.00, 120.00, 30.00, 60.00, 85.20, 12.50, 22.00
        # Total = 390.20
        assert stats["total_spent"] == 390.20
        assert stats["transaction_count"] == 8
        
        # Categories: Food (45.50 + 22.00 = 67.50), Transport (15.00), Bills (120.00), 
        # Health (30.00), Entertainment (60.00), Shopping (85.20), Other (12.50)
        # Top category should be "Bills" with 120.00
        assert stats["top_category"] == "Bills"

def test_get_user_stats_no_data():
    with app.app_context():
        # User 999 doesn't exist/has no expenses
        stats = get_user_stats(999)
        assert stats["total_spent"] == 0.0
        assert stats["transaction_count"] == 0
        assert stats["top_category"] == "N/A"

def test_get_category_breakdown():
    with app.app_context():
        # Demo user ID is 1
        breakdown = get_category_breakdown(1)
        
        # We expect 7 categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        assert len(breakdown) == 7
        
        # Check ordering (total DESC)
        # Bills (120.00), Shopping (85.20), Food (67.50), Entertainment (60.00), ...
        assert breakdown[0]["category"] == "Bills"
        assert breakdown[0]["total"] == 120.00
        assert breakdown[1]["category"] == "Shopping"
        assert breakdown[2]["category"] == "Food"

def test_get_category_breakdown_no_data():
    with app.app_context():
        # User 999 doesn't exist
        breakdown = get_category_breakdown(999)
        assert len(breakdown) == 0
