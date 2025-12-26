"""
FII API endpoint tests.

Tests for:
- POST /api/v1/fiis/ - Create FII
- GET /api/v1/fiis/ - List FIIs (with filtering/pagination)
- GET /api/v1/fiis/{pk} - Get single FII
- PATCH /api/v1/fiis/{pk} - Update FII
- DELETE /api/v1/fiis/{pk} - Soft delete FII
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from faker import Faker
from sqlalchemy.orm import Session

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
# CREATE FII ENDPOINT TESTS
# ============================================================================

class TestCreateFii:
    """Tests for POST /api/v1/fiis/"""

    def test_create_fii_success(
        self, authenticated_client: TestClient, test_user: User, db_session: Session
    ):
        """Test successful FII creation"""
        # Arrange
        fii_data = {
            "tag": "XPLG11",
            "name": "XP Log FII",
            "sector": "Logística",
        }

        # Act
        response = authenticated_client.post("/api/v1/fiis/", json=fii_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert_response_has_keys(
            data, ["pk", "tag", "name", "sector", "created_at", "updated_at"]
        )

        # Verify response values
        assert data["tag"] == fii_data["tag"]
        assert data["name"] == fii_data["name"]
        assert data["sector"] == fii_data["sector"]

        # Verify FII created in database
        fii = db_session.query(Fii).filter(Fii.tag == fii_data["tag"]).first()
        assert fii is not None
        assert_not_soft_deleted(fii)
        assert_audit_fields(fii, created_by_pk=test_user.pk)

    def test_create_fii_tag_normalized(
        self, authenticated_client: TestClient, db_session: Session
    ):
        """Test FII tag is uppercase normalized"""
        # Arrange
        fii_data = {
            "tag": "hglg11",  # lowercase - different from test_create_fii_success
            "name": "CSHG Logística FII",
            "sector": "Logística",
        }

        # Act
        response = authenticated_client.post("/api/v1/fiis/", json=fii_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["tag"] == "HGLG11"  # Uppercase

        # Verify in database
        fii = db_session.query(Fii).filter(Fii.tag == "HGLG11").first()
        assert fii is not None

    def test_create_fii_duplicate_tag(
        self, authenticated_client: TestClient, test_fii: Fii
    ):
        """Test creating FII with duplicate tag fails"""
        # Arrange
        fii_data = {
            "tag": test_fii.tag,  # Duplicate tag
            "name": "Another FII",
            "sector": "Shopping",
        }

        # Act
        response = authenticated_client.post("/api/v1/fiis/", json=fii_data)

        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_fii_unauthenticated(self, client: TestClient):
        """Test creating FII without authentication"""
        # Arrange
        fii_data = {
            "tag": "XPLG11",
            "name": "XP Log FII",
            "sector": "Logística",
        }

        # Act
        response = client.post("/api/v1/fiis/", json=fii_data)

        # Assert
        assert response.status_code == 403


# ============================================================================
# LIST FIIS ENDPOINT TESTS
# ============================================================================

class TestListFiis:
    """Tests for GET /api/v1/fiis/"""

    def test_list_fiis_success(
        self, authenticated_client: TestClient, test_fii: Fii
    ):
        """Test listing FIIs"""
        # Act
        response = authenticated_client.get("/api/v1/fiis/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify FII is in list
        fii_tags = [fii["tag"] for fii in data]
        assert test_fii.tag in fii_tags

    def test_list_fiis_pagination(
        self, authenticated_client: TestClient, multiple_test_fiis: list[Fii]
    ):
        """Test FII list pagination"""
        # Test skip parameter
        response = authenticated_client.get("/api/v1/fiis/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 5)

        # Test limit parameter
        response = authenticated_client.get("/api/v1/fiis/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert_pagination_params(data, 3)

    def test_list_fiis_filter_by_sector(
        self, authenticated_client: TestClient, fiis_multiple_sectors: dict
    ):
        """Test filtering FIIs by sector"""
        # Act - Filter by Logística
        response = authenticated_client.get("/api/v1/fiis/?sector=Logística")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # All returned FIIs should be Logística
        assert len(data) >= 2
        assert_list_contains_only(data, "sector", "Logística")

    def test_list_fiis_excludes_soft_deleted(
        self, authenticated_client: TestClient, test_fii: Fii, deleted_test_fii: Fii
    ):
        """Test soft deleted FIIs are excluded"""
        # Act
        response = authenticated_client.get("/api/v1/fiis/")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Active FII should be in list
        fii_tags = [fii["tag"] for fii in data]
        assert test_fii.tag in fii_tags

        # Deleted FII should NOT be in list
        assert deleted_test_fii.tag not in fii_tags

    def test_list_fiis_unauthenticated(self, client: TestClient):
        """Test listing FIIs without authentication"""
        # Act
        response = client.get("/api/v1/fiis/")

        # Assert
        assert response.status_code == 403

    def test_list_fiis_empty_result(self, authenticated_client: TestClient):
        """Test listing FIIs when none exist"""
        # Act
        response = authenticated_client.get("/api/v1/fiis/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# GET FII ENDPOINT TESTS
# ============================================================================

class TestGetFii:
    """Tests for GET /api/v1/fiis/{pk}"""

    def test_get_fii_success(
        self, authenticated_client: TestClient, test_fii: Fii
    ):
        """Test retrieving single FII"""
        # Act
        response = authenticated_client.get(f"/api/v1/fiis/{test_fii.pk}")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert_response_has_keys(
            data, ["pk", "tag", "name", "sector"]
        )

        # Verify response values
        assert data["pk"] == test_fii.pk
        assert data["tag"] == test_fii.tag
        assert data["name"] == test_fii.name
        assert data["sector"] == test_fii.sector

    def test_get_fii_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent FII"""
        # Act
        response = authenticated_client.get("/api/v1/fiis/99999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_fii_soft_deleted(
        self, authenticated_client: TestClient, deleted_test_fii: Fii
    ):
        """Test retrieving soft deleted FII"""
        # Act
        response = authenticated_client.get(f"/api/v1/fiis/{deleted_test_fii.pk}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_fii_unauthenticated(self, client: TestClient, test_fii: Fii):
        """Test retrieving FII without authentication"""
        # Act
        response = client.get(f"/api/v1/fiis/{test_fii.pk}")

        # Assert
        assert response.status_code == 403


# ============================================================================
# UPDATE FII ENDPOINT TESTS
# ============================================================================

class TestUpdateFii:
    """Tests for PATCH /api/v1/fiis/{pk}"""

    def test_update_fii_success(
        self,
        authenticated_client: TestClient,
        test_fii: Fii,
        test_user: User,
        db_session: Session,
    ):
        """Test updating FII"""
        # Arrange
        update_data = {
            "name": "Updated FII Name",
            "sector": "Shopping",
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/fiis/{test_fii.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response values
        assert data["name"] == update_data["name"]
        assert data["sector"] == update_data["sector"]

        # Verify updated in database
        db_session.refresh(test_fii)
        assert test_fii.name == update_data["name"]
        assert test_fii.sector == update_data["sector"]
        assert test_fii.updated_by_pk == test_user.pk

    def test_update_fii_partial(
        self, authenticated_client: TestClient, test_fii: Fii, db_session: Session
    ):
        """Test partial update (PATCH semantics)"""
        # Arrange
        original_sector = test_fii.sector
        update_data = {
            "name": "Partially Updated FII",
            # NOT updating sector
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/fiis/{test_fii.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Name should be updated
        assert data["name"] == update_data["name"]

        # Sector should remain unchanged
        assert data["sector"] == original_sector

        # Verify in database
        db_session.refresh(test_fii)
        assert test_fii.name == update_data["name"]
        assert test_fii.sector == original_sector

    def test_update_fii_duplicate_tag(
        self,
        authenticated_client: TestClient,
        test_fii: Fii,
        another_test_fii: Fii,
    ):
        """Test updating to duplicate tag fails"""
        # Arrange
        update_data = {
            "tag": another_test_fii.tag,  # Duplicate tag
        }

        # Act
        response = authenticated_client.patch(
            f"/api/v1/fiis/{test_fii.pk}", json=update_data
        )

        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_fii_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent FII"""
        # Arrange
        update_data = {
            "name": "Updated Name",
        }

        # Act
        response = authenticated_client.patch("/api/v1/fiis/99999", json=update_data)

        # Assert
        assert response.status_code == 404

    def test_update_fii_unauthenticated(self, client: TestClient, test_fii: Fii):
        """Test updating FII without authentication"""
        # Arrange
        update_data = {
            "name": "Updated Name",
        }

        # Act
        response = client.patch(f"/api/v1/fiis/{test_fii.pk}", json=update_data)

        # Assert
        assert response.status_code == 403


# ============================================================================
# DELETE FII ENDPOINT TESTS
# ============================================================================

class TestDeleteFii:
    """Tests for DELETE /api/v1/fiis/{pk}"""

    def test_delete_fii_success(
        self,
        authenticated_client: TestClient,
        test_fii: Fii,
        test_user: User,
        db_session: Session,
    ):
        """Test soft deleting FII"""
        # Arrange
        fii_pk = test_fii.pk

        # Act
        response = authenticated_client.delete(f"/api/v1/fiis/{fii_pk}")

        # Assert
        assert response.status_code == 204
        assert response.content == b""

        # Verify soft deleted in database
        db_session.expire_all()  # Force reload from database
        fii = db_session.query(Fii).filter(
            Fii.pk == fii_pk, Fii.rm_timestamp.is_(None)
        ).first()
        assert fii is None  # Should not be found (soft deleted)

        # Verify with include_deleted
        fii_with_deleted = db_session.query(Fii).filter(Fii.pk == fii_pk).first()
        assert fii_with_deleted is not None
        assert_soft_deleted(fii_with_deleted)
        assert fii_with_deleted.updated_by_pk == test_user.pk

    def test_delete_fii_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent FII"""
        # Act
        response = authenticated_client.delete("/api/v1/fiis/99999")

        # Assert
        assert response.status_code == 404

    def test_delete_fii_already_deleted(
        self, authenticated_client: TestClient, deleted_test_fii: Fii
    ):
        """Test deleting already deleted FII"""
        # Act
        response = authenticated_client.delete(f"/api/v1/fiis/{deleted_test_fii.pk}")

        # Assert
        assert response.status_code == 404

    def test_delete_fii_unauthenticated(self, client: TestClient, test_fii: Fii):
        """Test deleting FII without authentication"""
        # Act
        response = client.delete(f"/api/v1/fiis/{test_fii.pk}")

        # Assert
        assert response.status_code == 403
