"""
Test helper utilities.

This module provides helper functions for creating test data and asserting
expected behaviors in tests.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional
from faker import Faker
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models.dividend import Dividend
from app.db.models.fii import Fii
from app.db.models.fii_transaction import FiiTransaction
from app.db.models.user import User

# Initialize Faker
fake = Faker("pt_BR")


# ============================================================================
# USER HELPERS
# ============================================================================

def create_test_user(
    db_session: Session,
    email: Optional[str] = None,
    username: Optional[str] = None,
    password: str = "testpassword123",
    full_name: Optional[str] = None,
    is_active: bool = True,
    is_superuser: bool = False,
    **kwargs: Any
) -> User:
    """
    Create a test user with default or custom values.

    Args:
        db_session: Database session
        email: User email (auto-generated if None)
        username: Username (auto-generated if None)
        password: Plain password (default: "testpassword123")
        full_name: Full name (auto-generated if None)
        is_active: Whether user is active
        is_superuser: Whether user is superuser
        **kwargs: Additional fields to set on the user

    Returns:
        User: Created user instance
    """
    user = User(
        email=email or fake.email(),
        username=username or fake.user_name(),
        hashed_password=get_password_hash(password),
        full_name=full_name or fake.name(),
        is_active=is_active,
        is_superuser=is_superuser,
        **kwargs
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Store plain password for testing
    user.plain_password = password  # type: ignore

    return user


# ============================================================================
# FII HELPERS
# ============================================================================

def create_test_fii(
    db_session: Session,
    user_pk: int,
    tag: Optional[str] = None,
    name: Optional[str] = None,
    sector: str = "Logística",
    **kwargs: Any
) -> Fii:
    """
    Create a test FII with default or custom values.

    Args:
        db_session: Database session
        user_pk: User primary key for audit trail
        tag: FII tag/ticker (auto-generated if None)
        name: FII name (auto-generated if None)
        sector: FII sector
        **kwargs: Additional fields to set on the FII

    Returns:
        Fii: Created FII instance
    """
    fii = Fii(
        tag=tag or fake.lexify(text="????11").upper(),
        name=name or f"{fake.company()} FII",
        sector=sector,
        created_by_pk=user_pk,
        updated_by_pk=user_pk,
        **kwargs
    )

    db_session.add(fii)
    db_session.commit()
    db_session.refresh(fii)

    return fii


# ============================================================================
# TRANSACTION HELPERS
# ============================================================================

def create_test_transaction(
    db_session: Session,
    user_pk: int,
    fii_pk: int,
    transaction_type: str = "buy",
    transaction_date: Optional[date] = None,
    quantity: int = 100,
    price_per_unit: Optional[Decimal] = None,
    total_amount: Optional[Decimal] = None,
    **kwargs: Any
) -> FiiTransaction:
    """
    Create a test transaction with default or custom values.

    Args:
        db_session: Database session
        user_pk: User primary key (owner)
        fii_pk: FII primary key
        transaction_type: "buy" or "sell"
        transaction_date: Transaction date (default: 30 days ago)
        quantity: Number of units
        price_per_unit: Price per unit (auto-generated if None)
        total_amount: Total amount (auto-calculated if None)
        **kwargs: Additional fields to set on the transaction

    Returns:
        FiiTransaction: Created transaction instance
    """
    if price_per_unit is None:
        price_per_unit = Decimal(fake.pydecimal(left_digits=3, right_digits=2, positive=True))

    if total_amount is None:
        total_amount = Decimal(quantity) * price_per_unit

    if transaction_date is None:
        transaction_date = date.today() - timedelta(days=30)

    transaction = FiiTransaction(
        user_pk=user_pk,
        fii_pk=fii_pk,
        transaction_type=transaction_type,
        transaction_date=transaction_date,
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_amount=total_amount,
        created_by_pk=user_pk,
        updated_by_pk=user_pk,
        **kwargs
    )

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    return transaction


# ============================================================================
# DIVIDEND HELPERS
# ============================================================================

def create_test_dividend(
    db_session: Session,
    user_pk: int,
    fii_pk: int,
    payment_date: Optional[date] = None,
    reference_date: Optional[date] = None,
    amount_per_unit: Optional[Decimal] = None,
    units_held: int = 100,
    total_amount: Optional[Decimal] = None,
    **kwargs: Any
) -> Dividend:
    """
    Create a test dividend with default or custom values.

    Args:
        db_session: Database session
        user_pk: User primary key (owner)
        fii_pk: FII primary key
        payment_date: Payment date (default: 15 days ago)
        reference_date: Reference date (default: 30 days ago)
        amount_per_unit: Amount per unit (auto-generated if None)
        units_held: Number of units held
        total_amount: Total amount (auto-calculated if None)
        **kwargs: Additional fields to set on the dividend

    Returns:
        Dividend: Created dividend instance
    """
    if payment_date is None:
        payment_date = date.today() - timedelta(days=15)

    if reference_date is None:
        reference_date = date.today() - timedelta(days=30)

    if amount_per_unit is None:
        amount_per_unit = Decimal(fake.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.01, max_value=2.00))

    if total_amount is None:
        total_amount = Decimal(units_held) * amount_per_unit

    dividend = Dividend(
        user_pk=user_pk,
        fii_pk=fii_pk,
        payment_date=payment_date,
        reference_date=reference_date,
        amount_per_unit=amount_per_unit,
        units_held=units_held,
        total_amount=total_amount,
        created_by_pk=user_pk,
        updated_by_pk=user_pk,
        **kwargs
    )

    db_session.add(dividend)
    db_session.commit()
    db_session.refresh(dividend)

    return dividend


# ============================================================================
# ASSERTION HELPERS
# ============================================================================

def assert_audit_fields(
    obj: Any,
    created_by_pk: Optional[int],
    updated_by_pk: Optional[int] = None
) -> None:
    """
    Validate audit trail fields on a model instance.

    Args:
        obj: Model instance to validate
        created_by_pk: Expected created_by_pk value
        updated_by_pk: Expected updated_by_pk value (defaults to created_by_pk)

    Raises:
        AssertionError: If audit fields don't match expected values
    """
    if updated_by_pk is None:
        updated_by_pk = created_by_pk

    assert hasattr(obj, "created_by_pk"), f"{type(obj).__name__} missing created_by_pk field"
    assert hasattr(obj, "updated_by_pk"), f"{type(obj).__name__} missing updated_by_pk field"
    assert hasattr(obj, "created_at"), f"{type(obj).__name__} missing created_at field"
    assert hasattr(obj, "updated_at"), f"{type(obj).__name__} missing updated_at field"

    assert obj.created_by_pk == created_by_pk, \
        f"Expected created_by_pk={created_by_pk}, got {obj.created_by_pk}"
    assert obj.updated_by_pk == updated_by_pk, \
        f"Expected updated_by_pk={updated_by_pk}, got {obj.updated_by_pk}"
    assert obj.created_at is not None, "created_at should not be None"
    assert obj.updated_at is not None, "updated_at should not be None"


def assert_not_soft_deleted(obj: Any) -> None:
    """
    Verify that an object is NOT soft deleted.

    Args:
        obj: Model instance to validate

    Raises:
        AssertionError: If object is soft deleted (rm_timestamp is set)
    """
    assert hasattr(obj, "rm_timestamp"), f"{type(obj).__name__} missing rm_timestamp field"
    assert obj.rm_timestamp is None, f"{type(obj).__name__} should not be soft deleted"


def assert_soft_deleted(obj: Any) -> None:
    """
    Verify that an object IS soft deleted.

    Args:
        obj: Model instance to validate

    Raises:
        AssertionError: If object is NOT soft deleted (rm_timestamp is None)
    """
    assert hasattr(obj, "rm_timestamp"), f"{type(obj).__name__} missing rm_timestamp field"
    assert obj.rm_timestamp is not None, f"{type(obj).__name__} should be soft deleted"
    assert isinstance(obj.rm_timestamp, int), "rm_timestamp should be an integer (Unix epoch)"
    assert obj.rm_timestamp > 0, "rm_timestamp should be positive"


def assert_response_has_keys(response_data: dict, required_keys: list[str]) -> None:
    """
    Verify that a response dictionary contains all required keys.

    Args:
        response_data: Response data dictionary
        required_keys: List of required key names

    Raises:
        AssertionError: If any required key is missing
    """
    for key in required_keys:
        assert key in response_data, f"Response missing required key: {key}"


def assert_response_excludes_keys(response_data: dict, excluded_keys: list[str]) -> None:
    """
    Verify that a response dictionary does NOT contain excluded keys.

    Args:
        response_data: Response data dictionary
        excluded_keys: List of keys that should NOT be present

    Raises:
        AssertionError: If any excluded key is found
    """
    for key in excluded_keys:
        assert key not in response_data, f"Response should not contain key: {key}"


def assert_pagination_params(
    response_data: list,
    expected_length: int,
    message: str = ""
) -> None:
    """
    Verify pagination results.

    Args:
        response_data: List of results
        expected_length: Expected number of items
        message: Optional assertion message

    Raises:
        AssertionError: If length doesn't match
    """
    actual_length = len(response_data)
    assert actual_length == expected_length, \
        f"{message} Expected {expected_length} items, got {actual_length}"


def assert_list_contains_only(
    items: list[Any],
    field: str,
    expected_value: Any,
    message: str = ""
) -> None:
    """
    Verify that all items in a list have the same field value.

    Args:
        items: List of objects to check
        field: Field name to check
        expected_value: Expected value for the field
        message: Optional assertion message

    Raises:
        AssertionError: If any item has a different value
    """
    for i, item in enumerate(items):
        if isinstance(item, dict):
            actual_value = item.get(field)
        else:
            actual_value = getattr(item, field, None)

        assert actual_value == expected_value, \
            f"{message} Item {i}: expected {field}={expected_value}, got {actual_value}"


def assert_sorted_by(
    items: list[Any],
    field: str,
    descending: bool = False,
    message: str = ""
) -> None:
    """
    Verify that a list is sorted by a specific field.

    Args:
        items: List of objects to check
        field: Field name to check
        descending: Whether list should be descending (default: False)
        message: Optional assertion message

    Raises:
        AssertionError: If list is not sorted correctly
    """
    if len(items) < 2:
        return  # List of 0 or 1 items is always sorted

    for i in range(len(items) - 1):
        if isinstance(items[i], dict):
            current_value = items[i].get(field)
            next_value = items[i + 1].get(field)
        else:
            current_value = getattr(items[i], field)
            next_value = getattr(items[i + 1], field)

        if descending:
            assert current_value >= next_value, \
                f"{message} Items not sorted descending by {field}: {current_value} < {next_value} at index {i}"
        else:
            assert current_value <= next_value, \
                f"{message} Items not sorted ascending by {field}: {current_value} > {next_value} at index {i}"
