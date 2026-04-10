# Spendly — Personal Expense Tracker

Spendly is a Python/Flask-based web application designed to help users track their personal expenses. It features a modern Neo-Brutalist user interface and uses SQLite for data storage. The project is structured as a guided learning template, with several placeholder routes and database logic to be implemented.

## Core Technologies
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)
- **Database:** SQLite (SQLAlchemy is not used; direct SQLite interactions are expected)
- **Frontend:** HTML5, Jinja2 Templates, Vanilla CSS (Neo-Brutalist style), Vanilla JavaScript
- **Testing:** [pytest](https://docs.pytest.org/), `pytest-flask`

## Architecture
Spendly follows a monolithic Flask architecture:
- `app.py`: Central application file containing route definitions and Flask configuration.
- `database/db.py`: Modularized database logic for connection management and schema initialization.
- `templates/`: Jinja2 templates for rendering server-side views.
- `static/`: Public assets, including a comprehensive `style.css` defining the project's visual identity.

## Building and Running

### Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### Installation
1.  **Set up Virtual Environment:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
2.  **Install Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

### Execution
1.  **Run Application:**
    ```powershell
    python app.py
    ```
    The application defaults to `http://127.0.0.1:5001`.

2.  **Run Tests:**
    ```powershell
    pytest
    ```

## Development Conventions
- **Neo-Brutalist Styling:** Adhere to the established CSS variables and design language in `static/css/style.css` (e.g., solid shadows, thick borders, high contrast).
- **Vanilla JavaScript:** Prefer vanilla JavaScript for interactive elements (like the video modal on the landing page) over external libraries.
- **SQLite Primitives:** Database logic in `database/db.py` should focus on raw SQL queries and standard SQLite connection handling.
- **Incremental Implementation:** Follow the "Step" markers in comments (e.g., "Step 1 — Database Setup") when implementing new features.
