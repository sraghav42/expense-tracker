# Spec: Delete Expense

## Overview
This feature allows users to remove unwanted or incorrect expenses from their records. Providing a way to delete data is essential for maintaining an accurate financial history and gives users full control over their dashboard. This step completes the basic CRUD (Create, Read, Update, Delete) cycle for expenses.

## Depends on
- 01-database-setup.md (Schema and core helpers)
- 04-profile-page.md (Dashboard view)
- 07-add-expense.md (Expense creation)
- 08-edit-expense.md (Expense modification)

## Routes
- `GET /expenses/<int:id>/delete` — Renders a confirmation page before deletion — logged-in
- `POST /expenses/<int:id>/delete` — Executes the deletion from the database — logged-in

## Database changes
No database changes are required. This feature uses the existing `expenses` table.

## Templates
- **Create**: `templates/delete_confirm.html` — A simple page asking the user to confirm they want to delete the expense.
- **Modify**: `templates/profile.html` — Add a delete icon/link to each row in the recent activity table.
- **Modify**: `templates/edit_expense.html` — Add a "Delete Expense" button to the edit form for easier access.

## Files to change
- `app.py` — Implement the `delete_expense` route and a new POST route for deletion.
- `database/db.py` — Add `delete_expense(expense_id)` helper function.
- `templates/profile.html` — Add delete UI.
- `templates/edit_expense.html` — Add delete UI.

## Files to create
- `templates/delete_confirm.html`

## New dependencies
No new dependencies.

## Rules for implementation
- **Ownership Verification**: Before deleting, verify that the expense exists and belongs to the currently logged-in user (`g.user['id']`). Return `403 Forbidden` if it belongs to someone else, and `404 Not Found` if it doesn't exist.
- **CSRF Protection**: Use a POST request for the actual deletion to prevent accidental or malicious deletions via simple link clicks.
- **Flash Messages**: Provide clear feedback to the user (e.g., "Expense deleted successfully!") after the action is complete.
- **Redirects**: After deletion, always redirect the user back to the profile page.
- **Parameterized Queries**: Always use `?` placeholders in SQL queries to prevent SQL injection.
- **Consistency**: Use Lucide icons (`trash-2`) to match the existing design language.

## Definition of done
- [ ] Clicking a delete link in the dashboard opens a confirmation page.
- [ ] Deleting an expense that doesn't exist returns a 404 error.
- [ ] Deleting an expense owned by another user returns a 403 error.
- [ ] Confirming deletion removes the record from the database.
- [ ] After deletion, the user is redirected to the profile page with a success message.
- [ ] The deleted expense no longer appears in the dashboard stats or transaction list.
