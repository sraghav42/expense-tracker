# Spec: Login and Logout

## Overview
This feature implements the core authentication mechanism for Spendly. It allows registered users to securely log in using their email and password, and provides a way to end their session. It leverages Flask's session management to track the logged-in user across the application, which is essential for upcoming features like personalized profiles and expense tracking.

## Depends on
- Step 02: Registration

## Routes
- `GET /login` — Displays the login form — Public
- `POST /login` — Processes login data and authenticates the user — Public
- `GET /logout` — Ends the current session and redirects to the landing page — Logged-in

## Database changes
No database changes. Uses the existing `users` table.

## Templates
- **Modify**: `templates/login.html`
    - Ensure the form matches the required route (`/login`) and method (`POST`).
    - Use `url_for('login')` for the form action.
- **Modify**: `templates/base.html`
    - Conditionally show "Sign in" / "Get started" or "Sign out" links based on user authentication status.
    - If logged in, show a "Sign out" link using `url_for('logout')`.

## Files to change
- `app.py`:
    - Configure `app.secret_key` for session management.
    - Update the `/login` route to handle `POST` requests.
    - Implement authentication logic: verify password hash using `check_password_hash`.
    - Set the `user_id` in the `session` upon successful login.
    - Update the `/logout` route to clear the session.
    - Add a `before_request` or `context_processor` to make user data available to all templates if logged in.
- `templates/login.html`: Update the form and handle error messages.
- `templates/base.html`: Implement conditional navigation links.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Store `user_id` in Flask `session` for tracking logged-in state
- Ensure `app.secret_key` is set (for development, a hardcoded string is acceptable, but mention security in comments)
- Redirect authenticated users away from `/login` and `/register` to the landing page or profile

## Definition of done
- [ ] Navigating to `/login` shows the login form.
- [ ] Submitting the form with invalid credentials (wrong email or password) displays an error message.
- [ ] Submitting the form with valid credentials successfully logs the user in and redirects to the landing page (or a dashboard/profile if available).
- [ ] Once logged in, the navbar in `base.html` updates to show a "Sign out" link instead of "Sign in" and "Get started".
- [ ] Clicking the "Sign out" link clears the session and redirects to the landing page.
- [ ] Navigating to `/logout` manually while logged out redirects gracefully or handles the state without crashing.
- [ ] Logged-in state is persistent across page refreshes until logout.
