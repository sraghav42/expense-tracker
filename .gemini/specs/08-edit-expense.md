# Spec: Edit Expense

## Overview
The Edit Expense feature allows users to modify the details of previously recorded expenses. This is essential for correcting entry errors or updating transaction information. The feature provides a pre-populated form and ensures that all changes are validated and securely tied to the authenticated user before being persisted.

## Depends on
- 01-database-setup (Database schema)
- 02-registration (User model)
- 03-login-and-logout (Authentication/Session)
- 07-add-expense (Existing expenses and shared validation logic)

## Routes
- **GET /expenses/<int:id>/edit** — Renders the edit form populated with the current expense data — Logged-in
- **POST /expenses/<int:id>/edit** — Validates and updates the existing expense record — Logged-in

## Database changes
No schema changes. New helper functions in `database/db.py`:
- `get_expense_by_id(expense_id)`: Returns a single expense row.
- `update_expense(expense_id, amount, category, date, description)`: Updates an existing record.

## Templates
- **Create**: `templates/edit_expense.html` — A form similar to `add_expense.html` but pre-populated.
- **Modify**: `templates/profile.html` — Add an "Edit" link (icon or text) to each row in the transaction table.

## Files to change
- `app.py`: Implement the `GET` and `POST` logic for the edit route.
- `database/db.py`: Add the necessary helper functions.
- `templates/profile.html`: Update the transactions table to include action links.

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- **No SQLAlchemy or ORMs**: Use raw SQL via `database/db.py`.
- **Parameterized queries only**: Always use `?` placeholders to prevent SQL injection.
- **Ownership Check**: Ensure the expense being accessed belongs to `g.user['id']`. If not, use `abort(403)`.
- **Validation**: Reuse the validation logic from Step 07 (positive amount, required fields, allowed categories).
- **Aesthetics**: Use existing CSS variables and maintain consistency with the Spendly UI (cards, soft shadows, rounded corners).
- **Flash Messages**: Provide clear feedback on successful updates or validation errors.

## Definition of done
- [ ] Profile page includes an "Edit" link for every transaction.
- [ ] Clicking "Edit" navigates to the edit page with the form correctly pre-populated.
- [ ] Valid form submission updates the database and redirects to the profile page with a success message.
- [ ] Invalid submission (empty fields, non-positive amount) triggers a flash message and preserves input.
- [ ] Accessing the edit route for a non-existent ID or an ID belonging to another user returns a 404 or 403 error.
- [ ] The edit page is fully responsive and matches the Spendly design system.
