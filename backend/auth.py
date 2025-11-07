from flask_jwt_extended import create_access_token, create_refresh_token


def token_for(user):
    """Create an access JWT for the given user, storing the identity as a string.

    Accept either a User object or a plain integer id.
    """
    uid = getattr(user, "id", user)
    return create_access_token(identity=str(uid))


def refresh_for(user):
    """Create a refresh JWT for the given user (identity stored as string)."""
    uid = getattr(user, "id", user)
    return create_refresh_token(identity=str(uid))


def token_pair(user):
    """Return both access and refresh tokens for convenience."""
    return {"access_token": token_for(user), "refresh_token": refresh_for(user)}
