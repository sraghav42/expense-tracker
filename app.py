from flask import Flask, render_template, request, redirect, url_for, session, g
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'dev_key_for_session_management'

# Initialize and seed database on startup
with app.app_context():
    init_db()
    seed_db()


@app.before_request
def load_logged_in_user():
    """Load the user object from the database based on session data."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # 1. Check if passwords match
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        # 2. Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template("register.html", error="Email address already registered.")

        # 3. Create user
        hashed_password = generate_password_hash(password)
        create_user(name, email, hashed_password)

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Hardcoded data for Step 4 UI implementation
    user_data = {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "initials": "AS",
        "member_since": "January 2024"
    }

    stats = {
        "total_spent": "$1,250.00",
        "transaction_count": 12,
        "top_category": "Groceries"
    }

    transactions = [
        {"date": "2024-04-20", "description": "Weekly Groceries", "category": "Food", "amount": "$85.00"},
        {"date": "2024-04-18", "description": "Monthly Internet", "category": "Utilities", "amount": "$60.00"},
        {"date": "2024-04-15", "description": "Gas Station", "category": "Transport", "amount": "$45.00"}
    ]

    category_breakdown = [
        {"name": "Food", "total": "$450.00"},
        {"name": "Utilities", "total": "$300.00"},
        {"name": "Transport", "total": "$200.00"},
        {"name": "Entertainment", "total": "$150.00"},
        {"name": "Other", "total": "$150.00"}
    ]

    return render_template(
        "profile.html",
        user=user_data,
        stats=stats,
        transactions=transactions,
        categories=category_breakdown
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
