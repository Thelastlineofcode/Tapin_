# Tapin Backend (Flask API)

This folder contains the Flask API for the Tapin marketplace platform.

## Two Application Versions

- **`app.py`** - Full production application with authentication, JWT, database, listings, and all features
- **`mvp_app.py`** - Minimal MVP version with basic health check and in-memory items (for testing)

**Use `app.py` for development and production.**

## Prerequisites

- Python 3.10+ recommended
- virtualenv or venv

## Quick Start

**From the backend directory:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py upgrade  # Run database migrations
python seed_sample_data.py  # (Optional) Add sample data
python app.py
```

The API will be available at http://127.0.0.1:5000

### Test Endpoints

- Health check: http://127.0.0.1:5000/api/health
- Listings: http://127.0.0.1:5000/listings
- Items: http://127.0.0.1:5000/api/items

## Environment Variables

For local development, create a `.env` file in the repository root:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
SECURITY_PASSWORD_SALT=your-password-salt-here
SQLALCHEMY_DATABASE_URI=sqlite:///backend/data.db

# Optional: Email configuration for password resets
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_USE_TLS=true
```

See `CONFIG.md` for detailed configuration options and CI/CD setup.

## Database Management

### Running Migrations

Use the included manage.py wrapper to run migrations:

```bash
source .venv/bin/activate
python manage.py upgrade
```

### Creating New Migrations

When you modify database models:

```bash
alembic -c alembic.ini revision --autogenerate -m "description of changes"
python manage.py upgrade
```

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

## API Endpoints

### Public Endpoints

- `GET /api/health` - Health check
- `GET /api/items` - List items
- `POST /register` - Register new user
- `POST /login` - Login and get JWT tokens
- `POST /reset-password` - Request password reset
- `GET /listings` - Get all listings (supports ?q=search&location=filter)
- `GET /listings/<id>` - Get listing details

### Protected Endpoints (require JWT)

- `POST /api/items` - Create new item
- `POST /listings` - Create new listing
- `PUT /listings/<id>` - Update listing
- `DELETE /listings/<id>` - Delete listing
- `GET /me` - Get current user info
- `POST /refresh` - Refresh access token (requires refresh token)

See `API_DOCS.md` for complete API documentation.

## Database

- Development uses SQLite at `backend/data.db` (created automatically)
- For production, set `SQLALCHEMY_DATABASE_URI` to a PostgreSQL or MySQL connection string

## Notes

- This is a development prototype
- For production deployment:
  - Use a production RDBMS (PostgreSQL, MySQL)
  - Set strong secret keys via environment variables
  - Enable HTTPS
  - Configure proper CORS settings
  - Use production WSGI server (gunicorn, waitress)

This directory will contain the Flask backend for the Tapin project.

## Setup

1. Initialize a Python virtual environment.
2. Install Flask and other dependencies.
3. Implement API endpoints as described in the project documentation.
