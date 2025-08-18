import pytest
from datetime import datetime, timezone
from src.domain.entities.user import User


class TestUser:

    def test_user_creation_with_all_fields(self):
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True,
            created_at=created_at,
            updated_at=updated_at
        )
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.created_at == created_at
        assert user.updated_at == updated_at

    def test_user_creation_with_minimal_fields(self):
        user = User(
            id=None,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        assert user.id is None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_post_init_sets_timestamps(self):
        before_creation = datetime.now(timezone.utc)
        user = User(
            id=None,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        after_creation = datetime.now(timezone.utc)
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation

    def test_activate_user(self):
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=False
        )
        old_updated_at = user.updated_at
        import time
        time.sleep(0.001)
        user.activate()
        assert user.is_active is True
        assert user.updated_at > old_updated_at

    def test_deactivate_user(self):
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True
        )
        old_updated_at = user.updated_at
        import time
        time.sleep(0.001)
        user.deactivate()
        assert user.is_active is False
        assert user.updated_at > old_updated_at

    def test_update_password(self):
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="old_hashed_password"
        )
        old_updated_at = user.updated_at
        new_password = "new_hashed_password_456"
        import time
        time.sleep(0.001)
        user.update_password(new_password)
        assert user.hashed_password == new_password
        assert user.updated_at > old_updated_at

    def test_user_defaults(self):
        user = User(
            id=None,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_with_explicit_inactive_state(self):
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=False
        )
        assert user.is_active is False

    @pytest.mark.parametrize("email,username,password", [
        ("user1@example.com", "user1", "password1"),
        ("user2@test.org", "user2", "password2"),
        ("admin@company.com", "admin", "admin_password"),
    ])
    def test_user_creation_with_different_values(
        self,
        email: str,
        username: str,
        password: str
    ):
        user = User(
            id=None,
            email=email,
            username=username,
            hashed_password=password
        )
        assert user.email == email
        assert user.username == username
        assert user.hashed_password == password
        assert user.is_active is True
