from flask import Flask, render_template, request, redirect, url_for, session, g
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id, get_recent_transactions, get_user_stats, get_category_breakdown
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    if not g.user:
        return redirect(url_for("login"))

    # Format user info for the UI
    created_at = datetime.strptime(g.user["created_at"], "%Y-%m-%d %H:%M:%S")
    member_since = created_at.strftime("%B %Y")
    
    name_parts = g.user["name"].split()
    initials = "".join([part[0].upper() for part in name_parts[:2]])
    
    user_data = {
        "name": g.user["name"],
        "email": g.user["email"],
        "initials": initials,
        "member_since": member_since
    }

    stats_data = get_user_stats(g.user["id"])
    stats = {
        "total_spent": f"₹{stats_data['total_spent']:,.2f}",
        "transaction_count": stats_data["transaction_count"],
        "top_category": stats_data["top_category"]
    }

    db_transactions = get_recent_transactions(g.user["id"])
    transactions = [
        {
            "date": t["date"],
            "description": t["description"],
            "category": t["category"],
            "amount": f"₹{t['amount']:.2f}"
        }
        for t in db_transactions
    ]

    db_categories = get_category_breakdown(g.user["id"])
    total_spent_raw = stats_data['total_spent']
    category_breakdown = []
    
    for cat in db_categories:
        percentage = (cat["total"] / total_spent_raw * 100) if total_spent_raw > 0 else 0
        category_breakdown.append({
            "name": cat["category"],
            "total": f"₹{cat['total']:,.2f}",
            "percentage": percentage
        })

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
