import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash

DATABASE = 'spendly.db'

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    # Use Flask config if available (for tests), otherwise fallback to default
    db_path = current_app.config.get('DATABASE', DATABASE) if current_app else DATABASE
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_db():
    """Inserts sample data for development if the database is empty."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert demo user
    demo_email = "demo@spendly.com"
    demo_password_hash = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", demo_email, demo_password_hash)
    )
    user_id = cursor.lastrowid
    
    # Insert 8 sample expenses covering all categories
    # Food, Transport, Bills, Health, Entertainment, Shopping, Other
    sample_expenses = [
        (user_id, 45.50, "Food", "2026-04-01", "Grocery shopping"),
        (user_id, 15.00, "Transport", "2026-04-02", "Bus fare"),
        (user_id, 120.00, "Bills", "2026-04-03", "Electricity bill"),
        (user_id, 30.00, "Health", "2026-04-04", "Pharmacy"),
        (user_id, 60.00, "Entertainment", "2026-04-05", "Movie night"),
        (user_id, 85.20, "Shopping", "2026-04-06", "New clothes"),
        (user_id, 12.50, "Other", "2026-04-07", "Laundry"),
        (user_id, 22.00, "Food", "2026-04-08", "Lunch with friends")
    ]
    
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )
    
    conn.commit()
    conn.close()

def get_user_by_email(email):
    """Returns a user record by email, or None if not found."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(name, email, password_hash):
    """Inserts a new user into the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    """Returns a user record by ID, or None if not found."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_recent_transactions(user_id, date_from=None, date_to=None):
    """Returns a list of transactions for a given user ID, optionally filtered by date."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
        
    query += " ORDER BY date DESC, created_at DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_user_stats(user_id, date_from=None, date_to=None):
    """Returns a dictionary of summary statistics for a given user ID, optionally filtered by date."""
    conn = get_db()
    cursor = conn.cursor()
    
    query_base = "FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if date_from and date_to:
        query_base += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    
    # Get total spent and transaction count
    query_stats = "SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count " + query_base
    cursor.execute(query_stats, params)
    row = cursor.fetchone()
    total_spent = row['total_spent'] if row['total_spent'] is not None else 0.0
    transaction_count = row['transaction_count'] or 0
    
    # Get top category
    query_top = "SELECT category " + query_base + " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"
    cursor.execute(query_top, params)
    cat_row = cursor.fetchone()
    top_category = cat_row['category'] if cat_row else "N/A"
    
    conn.close()
    
    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category
    }

def get_category_breakdown(user_id, date_from=None, date_to=None):
    """Returns a list of categories and their total spending for a given user ID, optionally filtered by date."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
        
    query += " GROUP BY category ORDER BY total DESC"
    
    cursor.execute(query, params)
    breakdown = cursor.fetchall()
    conn.close()
    return breakdown
