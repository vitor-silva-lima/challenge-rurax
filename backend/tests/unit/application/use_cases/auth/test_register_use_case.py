import pytest
from unittest.mock import Mock
from src.application.use_cases.auth\
    .register_use_case import RegisterUserUseCase
from src.application.dtos.user_dto import UserCreateDTO
from src.domain.entities.user import User
from src.shared.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)


class TestRegisterUserUseCase:

    def setup_method(self):
        self.user_repository_mock = Mock()
        self.security_service_mock = Mock()
        self.use_case = RegisterUserUseCase(
            user_repository=self.user_repository_mock,
            security_service=self.security_service_mock
        )

    def test_register_user_success(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        hashed_password = "hashed_password_123"
        created_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password
        )
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password.return_value = hashed_password
        self.user_repository_mock.save.return_value = created_user
        result = self.use_case.execute(user_data)
        assert result == created_user
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.hashed_password == hashed_password
        self.user_repository_mock.get_by_email\
            .assert_called_once_with("test@example.com")
        self.user_repository_mock.get_by_username\
            .assert_called_once_with("testuser")
        self.security_service_mock.hash_password\
            .assert_called_once_with("password123")
        self.user_repository_mock.save.assert_called_once()

    def test_register_user_email_already_exists(self):
        user_data = UserCreateDTO(
            email="existing@example.com",
            username="testuser",
            password="password123"
        )
        existing_user = User(
            id=1,
            email="existing@example.com",
            username="existinguser",
            hashed_password="existing_hash"
        )
        self.user_repository_mock.get_by_email.return_value = existing_user
        with pytest.raises(EmailAlreadyExistsException) as exc_info:
            self.use_case.execute(user_data)
        assert str(exc_info.value) == "Email already exists"
        self.user_repository_mock.get_by_email\
            .assert_called_once_with("existing@example.com")
        self.user_repository_mock.get_by_username.assert_not_called()
        self.security_service_mock.hash_password.assert_not_called()
        self.user_repository_mock.save.assert_not_called()

    def test_register_user_username_already_exists(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="existinguser",
            password="password123"
        )
        existing_user = User(
            id=1,
            email="existing@example.com",
            username="existinguser",
            hashed_password="existing_hash"
        )
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = existing_user
        with pytest.raises(UsernameAlreadyExistsException) as exc_info:
            self.use_case.execute(user_data)
        assert str(exc_info.value) == "Username already exists"
        self.user_repository_mock.get_by_email\
            .assert_called_once_with("test@example.com")
        self.user_repository_mock.get_by_username\
            .assert_called_once_with("existinguser")
        self.security_service_mock.hash_password.assert_not_called()
        self.user_repository_mock.save.assert_not_called()

    def test_register_user_password_hashing(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="my_secret_password"
        )
        hashed_password = "super_secure_hash_123"
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password.return_value = hashed_password
        self.user_repository_mock.save.return_value = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password
        )
        result = self.use_case.execute(user_data)
        self.security_service_mock.hash_password\
            .assert_called_once_with("my_secret_password")
        assert result.hashed_password == hashed_password

    def test_register_user_created_user_structure(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        hashed_password = "hashed_password_123"
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password.return_value = hashed_password

        def capture_save_argument(user):
            assert user.id is None
            assert user.email == "test@example.com"
            assert user.username == "testuser"
            assert user.hashed_password == hashed_password
            assert user.is_active is True
            assert user.created_at is not None
            assert user.updated_at is not None
            user.id = 1
            return user

        self.user_repository_mock.save.side_effect = capture_save_argument
        result = self.use_case.execute(user_data)
        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.hashed_password == hashed_password

    @pytest.mark.parametrize("email,username,password", [
        ("user1@test.com", "user1", "password1"),
        ("user2@example.org", "user2", "password2"),
        ("admin@company.com", "admin", "admin_pass"),
    ])
    def test_register_user_with_different_data(
        self,
        email: str,
        username: str,
        password: str
    ):
        user_data = UserCreateDTO(
            email=email,
            username=username,
            password=password
        )
        hashed_password = f"hashed_{password}"
        created_user = User(
            id=1,
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password.return_value = hashed_password
        self.user_repository_mock.save.return_value = created_user
        result = self.use_case.execute(user_data)
        assert result.email == email
        assert result.username == username
        assert result.hashed_password == hashed_password
        self.security_service_mock.hash_password\
            .assert_called_once_with(password)

    def test_register_user_repository_error_handling(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password\
            .return_value = "hashed_password"
        self.user_repository_mock.save\
            .side_effect = Exception("Database error")
        with pytest.raises(Exception) as exc_info:
            self.use_case.execute(user_data)
        assert str(exc_info.value) == "Database error"

    def test_register_user_security_service_error_handling(self):
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        self.user_repository_mock.get_by_email.return_value = None
        self.user_repository_mock.get_by_username.return_value = None
        self.security_service_mock.hash_password\
            .side_effect = Exception("Hashing error")
        with pytest.raises(Exception) as exc_info:
            self.use_case.execute(user_data)
        assert str(exc_info.value) == "Hashing error"
        self.user_repository_mock.save.assert_not_called()
