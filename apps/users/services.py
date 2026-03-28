"""Business logic for user management.

All write operations on the User model should go through this service
to keep views thin and testable.
"""

import hashlib
import os

from .models import User


def _hash_password(raw_password: str) -> str:
    """Return a PBKDF2-SHA256 hex digest of the given password.

    In a production system, use Django's ``make_password`` / ``check_password``
    or a dedicated library such as ``bcrypt``.  This implementation is a
    self-contained demonstration compatible with the Django + SQLite setup
    required by the assignment.
    """
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", raw_password.encode(), salt.encode(), 260_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def create_user(name: str, email: str, raw_password: str) -> User:
    """Create and persist a new User with a hashed password."""
    user = User(
        name=name,
        email=email,
        password=_hash_password(raw_password),
    )
    user.full_clean()
    user.save()
    return user


def update_user(user: User, name: str, email: str, is_active: bool) -> User:
    """Update mutable fields on an existing User."""
    user.name = name
    user.email = email
    user.is_active = is_active
    user.full_clean()
    user.save(update_fields=["name", "email", "is_active"])
    return user


def delete_user(user: User) -> None:
    """Hard-delete a user record."""
    user.delete()
