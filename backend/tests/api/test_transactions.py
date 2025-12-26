"""
Transaction API endpoint tests.

Tests for:
- POST /api/v1/transactions/ - Create transaction
- GET /api/v1/transactions/ - List transactions (with filtering)
- GET /api/v1/transactions/{pk} - Get single transaction
- PATCH /api/v1/transactions/{pk} - Update transaction
- DELETE /api/v1/transactions/{pk} - Soft delete transaction
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session

from app.db.models.fii import Fii
from app.db.models.fii_transaction import FiiTransaction
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
# CREATE TRANSACTION ENDPOINT TESTS
# ============================================================================

class TestCreateTransaction:
    """Tests for POST /api/v1/transactions/"""

    def test_create_transaction_buy_success(
        self,
        authenticated_client: TestClient,
        test_fii: Fii,
        test_user: User,
        db_session: Session,
    ):
        """Test creating buy transaction"""
        # Arrange
        transaction_data = {
            "fii_pk": test_fii.pk,
            "transaction_type": "buy",
            "transaction_date": str(date.today() - timedelta(days=30)),
            "quantity": 100,
            "price_per_unit": "95.50",
            "total_amount": "9550.00",
        }

        # Act
        response = authenticated_client.post("/api/v1/transactions/", json=transaction_data)

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
                "transaction_type",
                "transaction_date",
                "quantity",
                "price_per_unit",
                "total_amount",
            ],
        )

        # Verify response values
        assert data["user_pk"] == test_user.pk  # Automatically set
        assert data["fii_pk"] == transaction_data["fii_pk"]
        assert data["transaction_type"] == transaction_data["transaction_type"]
        assert data["quantity"] == transaction_data["quantity"]

        # Verify transaction created in database
        transaction = db_session.query(FiiTransaction).filter(
            FiiTransaction.pk == data["pk"]
        ).first()
        assert transaction is not None
        assert transaction.user_pk == test_user.pk
        assert_not_soft_deleted(transaction)
        assert_audit_fields(transaction, created_by_pk=test_user.pk)

    def test_create_transaction_sell_success(
        self, authenticated_client: TestClient, test_fii: Fii, test_user: User
    ):
        """Test creating sell transaction"""
        # Arrange
        transaction_data = {
            "fii_pk": test_fii.pk,
            "transaction_type": "sell",
            "transaction_date": str(date.today() - timedelta(days=10)),
            "quantity": 50,
            "price_per_unit": "102.00",
            "total_amount": "5100.00",
        }

        # Act
        response = authenticated_client.post("/api/v1/transactions/", json=transaction_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_type"] == "sell"
        assert data["user_pk"] == test_user.pk

    def test_create_transaction_invalid_fii(self, authenticated_client: TestClient):
        """Test creating transaction with non-existent FII"""
        # Arrange
        transaction_data = {
            "fii_pk": 99999,  # Non-existent FII
            "transaction_type": "buy",
            "transaction_date": str(date.today() - timedelta(days=30)),
            "quantity": 100,
            "price_per_unit": "95.50",
            "total_amount": "9550.00",
        }

        # Act
        response = authenticated_client.post("/api/v1/transactions/", json=transaction_data)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_transaction_unauthenticated(self, client: TestClient, test_fii: Fii):
        """Test creating transaction without authentication"""
        # Arrange
        transaction_data = {
            "fii_pk": test_fii.pk,
            "transaction_type": "buy",
            "transaction_date": str(date.today() - timedelta(days=30)),
            "quantity": 100,
            "price_per_unit": "95.50",
            "total_amount": "9550.00",
        }

        # Act
        response = client.post("/api/v1/transactions/", json=transaction_data)

        # Assert
        assert response.status_code == 403


# ============================================================================
# LIST TRANSACTIONS ENDPOINT TESTS
# ============================================================================

class TestListTransactions:
    """Tests for GET /api/v1/transactions/"""

    def test_list_transactions_success(
        self, authenticated_client: TestClient, test_transaction: FiiTransaction
    ):
        """Test listing user's transactions"""
        # Act
        response = authenticated_client.get("/api/v1/transactions/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify transaction is in list
        transaction_pks = [t["pk"] for t in data]
        assert test_transaction.pk in transaction_pks

    def test_list_transactions_only_own(
        self,
        authenticated_client: TestClient,
        test_transaction: FiiTransaction,
        other_user_transaction: FiiTransaction,
    ):
        """Test user can only see their own transactions"""
        # Act
        response = authenticated_client.get("/api/v1/transactions/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Own transaction should be in list
        transaction_pks = [t["pk"] for t in data]
        assert test_transaction.pk in transaction_pks

        # Other user's transaction should NOT be in list
        assert other_user_transaction.pk not in transaction_pks

    def test_list_transactions_filter_by_fii(
        self, authenticated_client: TestClient, transactions_multiple_fiis: dict
    ):
        """Test filtering by FII"""
        # Arrange
        fii_pk = list(transactions_multiple_fiis.keys())[0]

        # Act
        response = authenticated_client.get(f"/api/v1/transactions/?fii_pk={fii_pk}")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # All returned transactions should be for specified FII
        assert len(data) >= 2
        assert_list_contains_only(data, "fii_pk", fii_pk)

    def test_list_transactions_filter_by_type(
        self, authenticated_client: TestClient, buy_and_sell_transactions: dict
    ):
        """Test filtering by transaction type"""
        # Act - Filter by "buy"
        response = authenticated_client.get("/api/v1/transactions/?transaction_type=buy")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # All returned transactions should be "buy"
        assert len(data) >= 2
        assert_list_contains_only(data, "transaction_type", "buy")

        # Act - Filter by "sell"
        response = authenticated_client.get("/api/v1/transactions/?transaction_type=sell")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # All returned transactions should be "sell"
        assert len(data) >= 2
        assert_list_contains_only(data, "transaction_type", "sell")

    def test_list_transactions_filter_by_date_range(
        self, authenticated_client: TestClient, transactions_various_dates: list[FiiTransaction]
    ):
        """Test filtering by date range"""
        # Arrange
        start_date = date.today() - timedelta(days=60)
        end_date = date.today() - timedelta(days=30)

        # Act
        response = authenticated_client.get(
            f"/api/v1/transactions/?start_date={start_date}&end_date={end_date}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify all transactions are within date range
        for transaction in data:
            transaction_date = date.fromisoformat(transaction["transaction_date"])
            assert start_date <= transaction_date <= end_date

    def test_list_transactions_pagination(
        self, authenticated_client: TestClient, many_transactions: list[FiiTransaction]
    ):
        """Test pagination"""
        # Test limit
        response = authenticated_client.get("/api/v1/transactions/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 5)

        # Test skip
        response = authenticated_client.get("/api/v1/transactions/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 5)

    def test_list_transactions_unauthenticated(self, client: TestClient):
        """Test listing transactions without authentication"""
        # Act
        response = client.get("/api/v1/transactions/")

        # Assert
        assert response.status_code == 403


# ============================================================================
# GET TRANSACTION ENDPOINT TESTS
# ============================================================================

class TestGetTransaction:
    """Tests for GET /api/v1/transactions/{pk}"""

    def test_get_transaction_success(
        self, authenticated_client: TestClient, test_transaction: FiiTransaction
    ):
        """Test retrieving single transaction"""
        # Act
        response = authenticated_client.get(f"/api/v1/transactions/{test_transaction.pk}")

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
                "transaction_type",
                "transaction_date",
                "quantity",
                "price_per_unit",
                "total_amount",
            ],
        )

        # Verify response values
        assert data["pk"] == test_transaction.pk
        assert data["fii_pk"] == test_transaction.fii_pk
        assert data["transaction_type"] == test_transaction.transaction_type

    def test_get_transaction_not_own(
        self, authenticated_client: TestClient, other_user_transaction: FiiTransaction
    ):
        """Test retrieving another user's transaction (ownership enforcement)"""
        # Act
        response = authenticated_client.get(f"/api/v1/transactions/{other_user_transaction.pk}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_transaction_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent transaction"""
        # Act
        response = authenticated_client.get("/api/v1/transactions/99999")

        # Assert
        assert response.status_code == 404

    def test_get_transaction_unauthenticated(
        self, client: TestClient, test_transaction: FiiTransaction
    ):
        """Test retrieving transaction without authentication"""
        # Act
        response = client.get(f"/api/v1/transactions/{test_transaction.pk}")

        # Assert
        assert response.status_code == 403


# ============================================================================
# UPDATE TRANSACTION ENDPOINT TESTS
# ============================================================================

class TestUpdateTransaction:
    """Tests for PATCH /api/v1/transactions/{pk}"""

    def test_update_transaction_success(
        self,
        authenticated_client: TestClient,
        test_transaction: FiiTransaction,
        test_user: User,
        db_session: Session,
    ):
        """Test updating transaction"""
        # Arrange
        update_data = {
            "quantity": 150,
            "price_per_unit": "98.00",
            "total_amount": "14700.00",
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/transactions/{test_transaction.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response values
        assert data["quantity"] == update_data["quantity"]
        assert Decimal(data["price_per_unit"]) == Decimal(update_data["price_per_unit"])

        # Verify updated in database
        db_session.refresh(test_transaction)
        assert test_transaction.quantity == update_data["quantity"]
        assert test_transaction.updated_by_pk == test_user.pk

    def test_update_transaction_not_own(
        self, authenticated_client: TestClient, other_user_transaction: FiiTransaction
    ):
        """Test updating another user's transaction"""
        # Arrange
        update_data = {
            "quantity": 200,
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/transactions/{other_user_transaction.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 404

    def test_update_transaction_invalid_fii(
        self, authenticated_client: TestClient, test_transaction: FiiTransaction
    ):
        """Test updating with invalid FII"""
        # Arrange
        update_data = {
            "fii_pk": 99999,  # Non-existent FII
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/transactions/{test_transaction.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_transaction_unauthenticated(
        self, client: TestClient, test_transaction: FiiTransaction
    ):
        """Test updating transaction without authentication"""
        # Arrange
        update_data = {
            "quantity": 200,
        }

        # Act
        response = client.patch(
            f"/api/v1/transactions/{test_transaction.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 403


# ============================================================================
# DELETE TRANSACTION ENDPOINT TESTS
# ============================================================================

class TestDeleteTransaction:
    """Tests for DELETE /api/v1/transactions/{pk}"""

    def test_delete_transaction_success(
        self,
        authenticated_client: TestClient,
        test_transaction: FiiTransaction,
        test_user: User,
        db_session: Session,
    ):
        """Test soft deleting transaction"""
        # Arrange
        transaction_pk = test_transaction.pk

        # Act
        response = authenticated_client.delete(f"/api/v1/transactions/{transaction_pk}")

        # Assert
        assert response.status_code == 204
        assert response.content == b""

        # Verify soft deleted in database
        db_session.expire_all()  # Force reload from database
        transaction = db_session.query(FiiTransaction).filter(
            FiiTransaction.pk == transaction_pk, FiiTransaction.rm_timestamp.is_(None)
        ).first()
        assert transaction is None  # Should not be found (soft deleted)

        # Verify with include_deleted
        transaction_with_deleted = db_session.query(FiiTransaction).filter(
            FiiTransaction.pk == transaction_pk
        ).first()
        assert transaction_with_deleted is not None
        assert_soft_deleted(transaction_with_deleted)

    def test_delete_transaction_not_own(
        self, authenticated_client: TestClient, other_user_transaction: FiiTransaction
    ):
        """Test deleting another user's transaction"""
        # Act
        response = authenticated_client.delete(f"/api/v1/transactions/{other_user_transaction.pk}")

        # Assert
        assert response.status_code == 404

    def test_delete_transaction_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent transaction"""
        # Act
        response = authenticated_client.delete("/api/v1/transactions/99999")

        # Assert
        assert response.status_code == 404

    def test_delete_transaction_unauthenticated(
        self, client: TestClient, test_transaction: FiiTransaction
    ):
        """Test deleting transaction without authentication"""
        # Act
        response = client.delete(f"/api/v1/transactions/{test_transaction.pk}")

        # Assert
        assert response.status_code == 403
