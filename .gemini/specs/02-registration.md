# Spec: Registration

## Overview
This feature implements the user registration process, allowing new users to create an account in Spendly. It handles form submission, validates input data (including email uniqueness and password confirmation), securely hashes passwords using `werkzeug.security`, and stores the new user in the database. This is a foundational step for personalized expense tracking.

## Depends on
- Step 01: Database Setup

## Routes
- `GET /register` — Displays the registration form — Public
- `POST /register` — Processes registration data and creates a new user — Public

## Database changes
No database changes. Uses the existing `users` table defined in `database/db.py`.

## Templates
- **Modify**: `templates/register.html`
    - Add a "Confirm password" field to the form.
    - Ensure all fields have clear labels and validation attributes.
    - Ensure the error message display block is properly utilized.

## Files to change
- `app.py`: 
    - Update the `/register` route to support `POST` method.
    - Implement logic for form validation and user creation.
    - Redirect to `/login` upon successful registration.
- `database/db.py`:
    - Implement `get_user_by_email(email)` to check for existing accounts.
    - Implement `create_user(name, email, password_hash)` to insert new users.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` for all database operations to ensure `PRAGMA foreign_keys = ON`
- Form validation must be handled on the server side (in `app.py`)
- Display user-friendly error messages for mismatched passwords or duplicate emails

## Definition of done
- [ ] Navigating to `/register` shows a registration form with Name, Email, Password, and Confirm Password fields.
- [ ] Submitting the form with empty fields triggers HTML5 validation or server-side errors.
- [ ] Submitting the form with mismatched passwords displays an error: "Passwords do not match."
- [ ] Submitting the form with an email that already exists in the database displays an error: "Email address already registered."
- [ ] Submitting valid data creates a new row in the `users` table.
- [ ] The password stored in the database is a secure hash, not plain text.
- [ ] Upon successful registration, the user is redirected to the `/login` page.
- [ ] The application remains functional and follows all PEP 8 standards.
