"""
Authentication API endpoint tests.

Tests for:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/refresh - Token refresh
- POST /api/v1/auth/logout - User logout
"""

import pytest
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session

from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from tests.utils.test_helpers import (
    assert_audit_fields,
    assert_not_soft_deleted,
    assert_response_excludes_keys,
    assert_response_has_keys,
    assert_soft_deleted,
    create_test_user,
)

fake = Faker("pt_BR")


# ============================================================================
# REGISTER ENDPOINT TESTS
# ============================================================================

class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register"""

    def test_register_success(self, client: TestClient, db_session: Session):
        """Test successful user registration"""
        # Arrange
        user_data = {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "StrongPassword123!",
            "full_name": fake.name(),
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert_response_has_keys(data, ["pk", "email", "username", "full_name", "is_active", "created_at"])
        assert_response_excludes_keys(data, ["password", "hashed_password"])

        # Verify response values
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True

        # Verify user created in database
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert_not_soft_deleted(user)

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email fails"""
        # Arrange
        user_data = {
            "email": test_user.email,  # Duplicate email
            "username": fake.user_name(),
            "password": "StrongPassword123!",
            "full_name": fake.name(),
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with existing username fails"""
        # Arrange
        user_data = {
            "email": fake.email(),
            "username": test_user.username,  # Duplicate username
            "password": "StrongPassword123!",
            "full_name": fake.name(),
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        assert "username already taken" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        # Arrange
        user_data = {
            "email": "not-an-email",
            "username": fake.user_name(),
            "password": "StrongPassword123!",
            "full_name": fake.name(),
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error


# ============================================================================
# LOGIN ENDPOINT TESTS
# ============================================================================

class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success_with_email(self, client: TestClient, test_user: User):
        """Test login with email"""
        # Arrange
        credentials = {
            "username": test_user.email,  # Can use email
            "password": test_user.plain_password,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert_response_has_keys(data, ["access_token", "refresh_token", "token_type"])
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_login_success_with_username(self, client: TestClient, test_user: User):
        """Test login with username"""
        # Arrange
        credentials = {
            "username": test_user.username,  # Can use username
            "password": test_user.plain_password,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify tokens returned
        assert_response_has_keys(data, ["access_token", "refresh_token", "token_type"])
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password"""
        # Arrange
        credentials = {
            "username": test_user.email,
            "password": "WrongPassword123!",
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        # Arrange
        credentials = {
            "username": "nonexistent@example.com",
            "password": "Password123!",
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client: TestClient, inactive_test_user: User):
        """Test login with inactive user"""
        # Arrange
        credentials = {
            "username": inactive_test_user.email,
            "password": inactive_test_user.plain_password,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 400
        assert "inactive user" in response.json()["detail"].lower()

    def test_login_creates_refresh_token(
        self, client: TestClient, test_user: User, db_session: Session
    ):
        """Test that login creates refresh token in database"""
        # Arrange
        credentials = {
            "username": test_user.email,
            "password": test_user.plain_password,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 200
        data = response.json()
        refresh_token_str = data["refresh_token"]

        # Verify refresh token in database
        refresh_token = (
            db_session.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token_str)
            .first()
        )
        assert refresh_token is not None
        assert refresh_token.user_pk == test_user.pk
        assert_not_soft_deleted(refresh_token)


# ============================================================================
# REFRESH ENDPOINT TESTS
# ============================================================================

class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh"""

    def test_refresh_success(
        self, client: TestClient, test_user_refresh_token: RefreshToken
    ):
        """Test successful token refresh"""
        # Arrange
        request_data = {
            "refresh_token": test_user_refresh_token.token_str,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/refresh", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify new tokens returned
        assert_response_has_keys(data, ["access_token", "refresh_token", "token_type"])
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)

        # New tokens should be different
        assert data["refresh_token"] != test_user_refresh_token.token_str  # type: ignore

    def test_refresh_revokes_old_token(
        self,
        client: TestClient,
        test_user_refresh_token: RefreshToken,
        db_session: Session,
    ):
        """Test that refresh revokes old token"""
        # Arrange
        old_token_pk = test_user_refresh_token.pk
        request_data = {
            "refresh_token": test_user_refresh_token.token_str,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/refresh", json=request_data)

        # Assert
        assert response.status_code == 200

        # Verify old token is soft deleted
        db_session.expire_all()  # Force reload from database
        old_token = db_session.query(RefreshToken).filter(
            RefreshToken.pk == old_token_pk,
            RefreshToken.rm_timestamp.is_(None),
        ).first()
        assert old_token is None  # Should not be found (soft deleted)

    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token"""
        # Arrange
        request_data = {
            "refresh_token": "invalid.token.string",
        }

        # Act
        response = client.post("/api/v1/auth/refresh", json=request_data)

        # Assert
        assert response.status_code == 401
        assert "invalid refresh token" in response.json()["detail"].lower()

    def test_refresh_nonexistent_token(self, client: TestClient):
        """Test refresh with non-existent token"""
        # Arrange
        # Create a valid JWT structure but not in database
        from app.core.security import create_refresh_token

        fake_token = create_refresh_token(data={"sub": "99999"})
        request_data = {
            "refresh_token": fake_token,
        }

        # Act
        response = client.post("/api/v1/auth/refresh", json=request_data)

        # Assert
        assert response.status_code == 401


# ============================================================================
# LOGOUT ENDPOINT TESTS
# ============================================================================

class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout"""

    def test_logout_success(
        self,
        client: TestClient,
        test_user_refresh_token: RefreshToken,
        db_session: Session,
    ):
        """Test successful logout"""
        # Arrange
        token_pk = test_user_refresh_token.pk
        request_data = {
            "refresh_token": test_user_refresh_token.token_str,  # type: ignore
        }

        # Act
        response = client.post("/api/v1/auth/logout", json=request_data)

        # Assert
        assert response.status_code == 204
        assert response.content == b""

        # Verify refresh token is soft deleted
        db_session.expire_all()  # Force reload from database
        token = db_session.query(RefreshToken).filter(
            RefreshToken.pk == token_pk,
            RefreshToken.rm_timestamp.is_(None),
        ).first()
        assert token is None  # Should not be found (soft deleted)

    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token (should still succeed)"""
        # Arrange
        request_data = {
            "refresh_token": "invalid.token.string",
        }

        # Act
        response = client.post("/api/v1/auth/logout", json=request_data)

        # Assert
        # Logout should succeed even with invalid token (idempotent)
        assert response.status_code == 204

    def test_logout_nonexistent_token(self, client: TestClient):
        """Test logout with non-existent token (should still succeed)"""
        # Arrange
        from app.core.security import create_refresh_token

        fake_token = create_refresh_token(data={"sub": "99999"})
        request_data = {
            "refresh_token": fake_token,
        }

        # Act
        response = client.post("/api/v1/auth/logout", json=request_data)

        # Assert
        # Logout should succeed even if token doesn't exist (idempotent)
        assert response.status_code == 204
