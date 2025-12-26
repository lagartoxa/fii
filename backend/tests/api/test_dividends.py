"""
Dividend API endpoint tests.

Tests for:
- POST /api/v1/dividends/ - Create dividend
- GET /api/v1/dividends/ - List dividends (with filtering)
- GET /api/v1/dividends/{pk} - Get single dividend
- PATCH /api/v1/dividends/{pk} - Update dividend
- DELETE /api/v1/dividends/{pk} - Soft delete dividend
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session

from app.db.models.dividend import Dividend
from app.db.models.fii import Fii
from app.db.models.user import User
from tests.utils.test_helpers import (
    assert_audit_fields,
    assert_list_contains_only,
    assert_not_soft_deleted,
    assert_pagination_params,
    assert_response_has_keys,
    assert_soft_deleted,
)

fake = Faker("pt_BR")


# ============================================================================
# CREATE DIVIDEND ENDPOINT TESTS
# ============================================================================

class TestCreateDividend:
    """Tests for POST /api/v1/dividends/"""

    def test_create_dividend_success(
        self,
        authenticated_client: TestClient,
        test_fii: Fii,
        test_user: User,
        db_session: Session,
    ):
        """Test creating dividend"""
        # Arrange
        dividend_data = {
            "fii_pk": test_fii.pk,
            "payment_date": str(date.today() - timedelta(days=15)),
            "amount_per_unit": "0.85",
        }

        # Act
        response = authenticated_client.post("/api/v1/dividends/", json=dividend_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert_response_has_keys(
            data,
            [
                "pk",
                "user_pk",
                "fii_pk",
                "payment_date",
                "amount_per_unit",
            ],
        )

        # Verify response values
        assert data["user_pk"] == test_user.pk  # Automatically set
        assert data["fii_pk"] == dividend_data["fii_pk"]
        assert Decimal(data["amount_per_unit"]) == Decimal(dividend_data["amount_per_unit"])

        # Verify dividend created in database
        dividend = db_session.query(Dividend).filter(Dividend.pk == data["pk"]).first()
        assert dividend is not None
        assert dividend.user_pk == test_user.pk
        assert_not_soft_deleted(dividend)
        assert_audit_fields(dividend, created_by_pk=test_user.pk)

    def test_create_dividend_invalid_fii(self, authenticated_client: TestClient):
        """Test creating dividend with non-existent FII"""
        # Arrange
        dividend_data = {
            "fii_pk": 99999,  # Non-existent FII
            "payment_date": str(date.today() - timedelta(days=15)),
            "reference_date": str(date.today() - timedelta(days=30)),
            "amount_per_unit": "0.85",
            "total_amount": "85.00",
        }

        # Act
        response = authenticated_client.post("/api/v1/dividends/", json=dividend_data)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_dividend_unauthenticated(self, client: TestClient, test_fii: Fii):
        """Test creating dividend without authentication"""
        # Arrange
        dividend_data = {
            "fii_pk": test_fii.pk,
            "payment_date": str(date.today() - timedelta(days=15)),
            "amount_per_unit": "0.85",
        }

        # Act
        response = client.post("/api/v1/dividends/", json=dividend_data)

        # Assert
        assert response.status_code == 403


# ============================================================================
# LIST DIVIDENDS ENDPOINT TESTS
# ============================================================================

class TestListDividends:
    """Tests for GET /api/v1/dividends/"""

    def test_list_dividends_success(
        self, authenticated_client: TestClient, test_dividend: Dividend
    ):
        """Test listing user's dividends"""
        # Act
        response = authenticated_client.get("/api/v1/dividends/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify dividend is in list
        dividend_pks = [d["pk"] for d in data]
        assert test_dividend.pk in dividend_pks

    def test_list_dividends_only_own(
        self,
        authenticated_client: TestClient,
        test_dividend: Dividend,
        other_user_dividend: Dividend,
    ):
        """Test user can only see their own dividends"""
        # Act
        response = authenticated_client.get("/api/v1/dividends/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Own dividend should be in list
        dividend_pks = [d["pk"] for d in data]
        assert test_dividend.pk in dividend_pks

        # Other user's dividend should NOT be in list
        assert other_user_dividend.pk not in dividend_pks

    def test_list_dividends_filter_by_fii(
        self, authenticated_client: TestClient, dividends_multiple_fiis: dict
    ):
        """Test filtering by FII"""
        # Arrange
        fii_pk = list(dividends_multiple_fiis.keys())[0]

        # Act
        response = authenticated_client.get(f"/api/v1/dividends/?fii_pk={fii_pk}")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # All returned dividends should be for specified FII
        assert len(data) >= 2
        assert_list_contains_only(data, "fii_pk", fii_pk)

    def test_list_dividends_filter_by_date_range(
        self, authenticated_client: TestClient, dividends_various_dates: list[Dividend]
    ):
        """Test filtering by date range"""
        # Arrange
        start_date = date.today() - timedelta(days=60)
        end_date = date.today() - timedelta(days=30)

        # Act
        response = authenticated_client.get(
            f"/api/v1/dividends/?start_date={start_date}&end_date={end_date}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify all dividends are within date range
        for dividend in data:
            payment_date = date.fromisoformat(dividend["payment_date"])
            assert start_date <= payment_date <= end_date

    def test_list_dividends_pagination(
        self, authenticated_client: TestClient, many_dividends: list[Dividend]
    ):
        """Test pagination"""
        # Test limit
        response = authenticated_client.get("/api/v1/dividends/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 5)

        # Test skip
        response = authenticated_client.get("/api/v1/dividends/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 5)

    def test_list_dividends_unauthenticated(self, client: TestClient):
        """Test listing dividends without authentication"""
        # Act
        response = client.get("/api/v1/dividends/")

        # Assert
        assert response.status_code == 403


# ============================================================================
# GET DIVIDEND ENDPOINT TESTS
# ============================================================================

class TestGetDividend:
    """Tests for GET /api/v1/dividends/{pk}"""

    def test_get_dividend_success(
        self, authenticated_client: TestClient, test_dividend: Dividend
    ):
        """Test retrieving single dividend"""
        # Act
        response = authenticated_client.get(f"/api/v1/dividends/{test_dividend.pk}")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert_response_has_keys(
            data,
            [
                "pk",
                "user_pk",
                "fii_pk",
                "payment_date",
                "amount_per_unit",
            ],
        )

        # Verify response values
        assert data["pk"] == test_dividend.pk
        assert data["fii_pk"] == test_dividend.fii_pk

    def test_get_dividend_not_own(
        self, authenticated_client: TestClient, other_user_dividend: Dividend
    ):
        """Test retrieving another user's dividend (ownership enforcement)"""
        # Act
        response = authenticated_client.get(f"/api/v1/dividends/{other_user_dividend.pk}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_dividend_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent dividend"""
        # Act
        response = authenticated_client.get("/api/v1/dividends/99999")

        # Assert
        assert response.status_code == 404

    def test_get_dividend_unauthenticated(
        self, client: TestClient, test_dividend: Dividend
    ):
        """Test retrieving dividend without authentication"""
        # Act
        response = client.get(f"/api/v1/dividends/{test_dividend.pk}")

        # Assert
        assert response.status_code == 403


# ============================================================================
# UPDATE DIVIDEND ENDPOINT TESTS
# ============================================================================

class TestUpdateDividend:
    """Tests for PATCH /api/v1/dividends/{pk}"""

    def test_update_dividend_success(
        self,
        authenticated_client: TestClient,
        test_dividend: Dividend,
        test_user: User,
        db_session: Session,
    ):
        """Test updating dividend"""
        # Arrange
        update_data = {
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/dividends/{test_dividend.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response values

        # Verify updated in database
        db_session.refresh(test_dividend)
        assert test_dividend.updated_by_pk == test_user.pk

    def test_update_dividend_not_own(
        self, authenticated_client: TestClient, other_user_dividend: Dividend
    ):
        """Test updating another user's dividend"""
        # Arrange
        update_data = {
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/dividends/{other_user_dividend.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 404

    def test_update_dividend_invalid_fii(
        self, authenticated_client: TestClient, test_dividend: Dividend
    ):
        """Test updating with invalid FII"""
        # Arrange
        update_data = {
            "fii_pk": 99999,  # Non-existent FII
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/dividends/{test_dividend.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_dividend_unauthenticated(
        self, client: TestClient, test_dividend: Dividend
    ):
        """Test updating dividend without authentication"""
        # Arrange
        update_data = {
        }

        # Act
        response = client.patch(f"/api/v1/dividends/{test_dividend.pk}", json=update_data)

        # Assert
        assert response.status_code == 403


# ============================================================================
# DELETE DIVIDEND ENDPOINT TESTS
# ============================================================================

class TestDeleteDividend:
    """Tests for DELETE /api/v1/dividends/{pk}"""

    def test_delete_dividend_success(
        self,
        authenticated_client: TestClient,
        test_dividend: Dividend,
        test_user: User,
        db_session: Session,
    ):
        """Test soft deleting dividend"""
        # Arrange
        dividend_pk = test_dividend.pk

        # Act
        response = authenticated_client.delete(f"/api/v1/dividends/{dividend_pk}")

        # Assert
        assert response.status_code == 204
        assert response.content == b""

        # Verify soft deleted in database
        db_session.expire_all()  # Force reload from database
        dividend = db_session.query(Dividend).filter(
            Dividend.pk == dividend_pk, Dividend.rm_timestamp.is_(None)
        ).first()
        assert dividend is None  # Should not be found (soft deleted)

        # Verify with include_deleted
        dividend_with_deleted = db_session.query(Dividend).filter(
            Dividend.pk == dividend_pk
        ).first()
        assert dividend_with_deleted is not None
        assert_soft_deleted(dividend_with_deleted)

    def test_delete_dividend_not_own(
        self, authenticated_client: TestClient, other_user_dividend: Dividend
    ):
        """Test deleting another user's dividend"""
        # Act
        response = authenticated_client.delete(f"/api/v1/dividends/{other_user_dividend.pk}")

        # Assert
        assert response.status_code == 404

    def test_delete_dividend_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent dividend"""
        # Act
        response = authenticated_client.delete("/api/v1/dividends/99999")

        # Assert
        assert response.status_code == 404

    def test_delete_dividend_unauthenticated(
        self, client: TestClient, test_dividend: Dividend
    ):
        """Test deleting dividend without authentication"""
        # Act
        response = client.delete(f"/api/v1/dividends/{test_dividend.pk}")

        # Assert
        assert response.status_code == 403
