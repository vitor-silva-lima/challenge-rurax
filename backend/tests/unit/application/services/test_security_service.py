import pytest
from unittest.mock import Mock
from datetime import timedelta
from abc import ABC
from src.application.services.security_service import SecurityService


class TestSecurityServiceInterface:

    def setup_method(self):
        self.security_service_mock = Mock(spec=SecurityService)

    def test_security_service_is_abstract(self):
        assert issubclass(SecurityService, ABC)

    def test_hash_password_method_signature(self):
        password = "test_password"
        expected_hash = "hashed_password_123"
        self.security_service_mock.hash_password.return_value = expected_hash
        result = self.security_service_mock.hash_password(password)
        assert result == expected_hash
        self.security_service_mock.hash_password\
            .assert_called_once_with(password)

    def test_verify_password_method_signature(self):
        plain_password = "test_password"
        hashed_password = "hashed_password_123"
        self.security_service_mock.verify_password.return_value = True
        result = self.security_service_mock\
            .verify_password(plain_password, hashed_password)
        assert result is True
        self.security_service_mock.verify_password\
            .assert_called_once_with(plain_password, hashed_password)

    def test_verify_password_returns_boolean(self):
        self.security_service_mock.verify_password.return_value = True
        result_true = self.security_service_mock\
            .verify_password("correct", "hash")
        assert isinstance(result_true, bool)
        assert result_true is True
        self.security_service_mock.verify_password.return_value = False
        result_false = self.security_service_mock\
            .verify_password("wrong", "hash")
        assert isinstance(result_false, bool)
        assert result_false is False

    def test_create_access_token_method_signature(self):
        subject = "user123"
        expires_delta = timedelta(hours=1)
        expected_token = "jwt_token_123"
        self.security_service_mock.create_access_token\
            .return_value = expected_token
        result = self.security_service_mock\
            .create_access_token(subject, expires_delta)
        assert result == expected_token
        self.security_service_mock.create_access_token\
            .assert_called_once_with(subject, expires_delta)

    def test_create_access_token_without_expires_delta(self):
        subject = "user123"
        expected_token = "jwt_token_default"
        self.security_service_mock.create_access_token\
            .return_value = expected_token
        result = self.security_service_mock\
            .create_access_token(subject)
        assert result == expected_token
        self.security_service_mock.create_access_token\
            .assert_called_once_with(subject)

    def test_create_access_token_with_none_expires_delta(self):
        subject = "user123"
        expected_token = "jwt_token_none"
        self.security_service_mock.create_access_token\
            .return_value = expected_token
        result = self.security_service_mock\
            .create_access_token(subject, None)
        assert result == expected_token
        self.security_service_mock.create_access_token\
            .assert_called_once_with(subject, None)

    def test_verify_token_method_signature(self):
        token = "jwt_token_123"
        expected_subject = "user123"
        self.security_service_mock.verify_token.return_value = expected_subject
        result = self.security_service_mock.verify_token(token)
        assert result == expected_subject
        self.security_service_mock.verify_token.assert_called_once_with(token)

    def test_verify_token_returns_optional_string(self):
        self.security_service_mock.verify_token.return_value = "user123"
        result_valid = self.security_service_mock.verify_token("valid_token")
        assert isinstance(result_valid, str)
        assert result_valid == "user123"
        self.security_service_mock.verify_token.return_value = None
        result_invalid = self.security_service_mock\
            .verify_token("invalid_token")
        assert result_invalid is None

    @pytest.mark.parametrize("password", [
        "short123",
        "medium_password_123",
        "very_long_password_with_special_chars_!@#$%^&*()",
        "123456",
        "password",
    ])
    def test_hash_password_with_different_passwords(self, password):
        expected_hash = f"hashed_{password}"
        self.security_service_mock.hash_password.return_value = expected_hash
        result = self.security_service_mock.hash_password(password)
        assert result == expected_hash
        self.security_service_mock.hash_password\
            .assert_called_once_with(password)
        self.security_service_mock.reset_mock()

    @pytest.mark.parametrize("subject,expires_hours", [
        ("user1", 1),
        ("user2", 24),
        ("admin", 2),
        ("guest", 0.5),
    ])
    def test_create_access_token_with_different_subjects_and_expiry(
        self,
        subject: str,
        expires_hours: int
    ):
        expires_delta = timedelta(hours=expires_hours)
        expected_token = f"token_for_{subject}_{expires_hours}h"
        self.security_service_mock.create_access_token\
            .return_value = expected_token
        result = self.security_service_mock\
            .create_access_token(subject, expires_delta)
        assert result == expected_token
        self.security_service_mock.create_access_token\
            .assert_called_once_with(subject, expires_delta)
        self.security_service_mock.reset_mock()

    def test_password_verification_workflow(self):
        original_password = "my_secret_password"
        hashed_password = "hashed_my_secret_password"
        self.security_service_mock.hash_password.return_value = hashed_password
        self.security_service_mock.verify_password.return_value = True
        hash_result = self.security_service_mock\
            .hash_password(original_password)
        verify_result = self.security_service_mock\
            .verify_password(original_password, hash_result)
        assert hash_result == hashed_password
        assert verify_result is True
        self.security_service_mock.hash_password\
            .assert_called_once_with(original_password)
        self.security_service_mock.verify_password\
            .assert_called_once_with(original_password, hashed_password)

    def test_token_creation_and_verification_workflow(self):
        subject = "user123"
        expires_delta = timedelta(hours=1)
        token = "jwt_token_123"
        self.security_service_mock.create_access_token.return_value = token
        self.security_service_mock.verify_token.return_value = subject
        created_token = self.security_service_mock\
            .create_access_token(subject, expires_delta)
        verified_subject = self.security_service_mock\
            .verify_token(created_token)
        assert created_token == token
        assert verified_subject == subject
        self.security_service_mock.create_access_token\
            .assert_called_once_with(subject, expires_delta)
        self.security_service_mock.verify_token\
            .assert_called_once_with(token)

    def test_security_service_method_calls_tracking(self):
        self.security_service_mock.hash_password("password1")
        self.security_service_mock.hash_password("password2")
        self.security_service_mock.verify_password("plain", "hash")
        self.security_service_mock.create_access_token("user")
        self.security_service_mock.verify_token("token")
        assert self.security_service_mock.hash_password.call_count == 2
        assert self.security_service_mock.verify_password.call_count == 1
        assert self.security_service_mock.create_access_token.call_count == 1
        assert self.security_service_mock.verify_token.call_count == 1

    def test_security_service_all_methods_exist(self):
        assert hasattr(SecurityService, 'hash_password')
        assert hasattr(SecurityService, 'verify_password')
        assert hasattr(SecurityService, 'create_access_token')
        assert hasattr(SecurityService, 'verify_token')
        assert getattr(
            SecurityService.hash_password, '__isabstractmethod__', False)
        assert getattr(
            SecurityService.verify_password, '__isabstractmethod__', False)
        assert getattr(
            SecurityService.create_access_token, '__isabstractmethod__', False)
        assert getattr(
            SecurityService.verify_token, '__isabstractmethod__', False)
