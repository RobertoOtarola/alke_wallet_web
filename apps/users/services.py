"""Business logic for user management.

All write operations on the User model should go through this service
to keep views thin and testable.
"""

from .models import User


def create_user(name: str, email: str, raw_password: str) -> User:
    """Create and persist a new User with a hashed password."""
    user = User(
        name=name,
        email=email,
    )
    user.set_password(raw_password)
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
