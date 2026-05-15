# Spec: Add Expense

## Overview
This feature allows users to record new expenses by providing an amount, category, date, and description. It is the core data entry point for the application, enabling users to build their financial history and see their statistics update in real-time on the profile page.

## Depends on
- Step 01: Database Setup (for the expenses table)
- Step 03: Login and Logout (for authentication and user context)
- Step 04: Profile Page (for navigation)

## Routes
- `GET /expenses/add` — Display the add expense form — Logged-in
- `POST /expenses/add` — Process the form submission and save the expense — Logged-in

## Database changes
No schema changes are required as the `expenses` table was created in Step 01.
The following helper function needs to be added to `database/db.py`:
- `add_expense(user_id, amount, category, date, description)`: Inserts a new record into the `expenses` table.

## Templates
- **Create**: `templates/add_expense.html` — The form for entering expense details.
- **Modify**: `templates/profile.html` — Add a prominent "Add Expense" button in the header or summary section.

## Files to change
- `app.py`: Implement the `GET` and `POST` logic for `/expenses/add`.
- `database/db.py`: Add the `add_expense` helper function.
- `templates/profile.html`: Add navigation link to the new route.

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only (use `?` placeholders).
- Passwords hashed with werkzeug (not applicable here, but part of standard rules).
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Use `flash()` for success/error messages upon form submission.
- Ensure the Category field is a dropdown with the standard options: Food, Transport, Bills, Health, Entertainment, Shopping, Other.

## Definition of done
- [ ] User can navigate to the "Add Expense" page from the profile dashboard.
- [ ] The "Add Expense" form is visually consistent with the rest of the application.
- [ ] Form validation prevents submission of empty amounts or descriptions.
- [ ] Submitting a valid expense redirects the user to the profile page with a success message.
- [ ] The newly added expense is immediately visible in the "Recent Transactions" table.
- [ ] Stats (Total Spent, Transaction Count) on the profile page update correctly after adding an expense.
