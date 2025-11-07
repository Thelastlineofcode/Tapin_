import pytest
from uuid import uuid4

from app import app, db, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        # Clean up DB between tests to ensure isolation
        db.session.remove()
        db.drop_all()


@pytest.fixture
def create_user():
    def _create(email=None, password="password"):
        with app.app_context():
            if email is None:
                email = f"user+{uuid4().hex}@example.com"
            user = User(email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create
