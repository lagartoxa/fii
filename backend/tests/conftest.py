"""
Test configuration and fixtures.

This module provides pytest fixtures for database sessions, FastAPI test clients,
authentication, and test data creation.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.models.dividend import Dividend
from app.db.models.fii import Fii
from app.db.models.fii_transaction import FiiTransaction
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.repositories.dividend_repository import DividendRepository
from app.db.repositories.fii_repository import FiiRepository
from app.db.repositories.fii_transaction_repository import FiiTransactionRepository
from app.db.repositories.user_repository import UserRepository
from app.main import app
from app.api.deps import get_db

# Initialize Faker
fake = Faker("pt_BR")  # Brazilian Portuguese for realistic FII data


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_engine():
    """
    Create test database engine (session-scoped).

    Uses SQLite in-memory database for fast, isolated tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Create fresh database session for each test (function-scoped).

    Each test gets a clean database state with automatic rollback after test.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    session = TestingSessionLocal()

    yield session

    # Rollback any uncommitted changes
    session.rollback()
    session.close()


# ============================================================================
# FASTAPI CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def client(db_session: Session):
    """
    FastAPI TestClient with database override (unauthenticated).

    Returns a test client that uses the test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client: TestClient, test_user_token: str):
    """
    FastAPI TestClient with authentication header.

    Returns a test client with JWT token set in Authorization header.
    """
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db_session: Session):
    """
    Create test user with default credentials.

    Returns:
        User: Test user with pk, email, username, is_active=True
    """
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        hashed_password=get_password_hash("testpassword123"),
        full_name=fake.name(),
        is_active=True,
        is_superuser=False,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Store plain password for login tests
    user.plain_password = "testpassword123"  # type: ignore

    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """
    Generate JWT access token for test user.

    Returns:
        str: JWT access token
    """
    return create_access_token(data={"sub": str(test_user.pk)})


@pytest.fixture
def inactive_test_user(db_session: Session):
    """
    Create inactive test user.

    Returns:
        User: Inactive user with is_active=False
    """
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        hashed_password=get_password_hash("testpassword123"),
        full_name=fake.name(),
        is_active=False,
        is_superuser=False,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user.plain_password = "testpassword123"  # type: ignore

    return user


@pytest.fixture
def another_test_user(db_session: Session):
    """
    Create second test user for ownership tests.

    Returns:
        User: Another test user
    """
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        hashed_password=get_password_hash("anotherpassword123"),
        full_name=fake.name(),
        is_active=True,
        is_superuser=False,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user.plain_password = "anotherpassword123"  # type: ignore

    return user


# ============================================================================
# FII FIXTURES
# ============================================================================

@pytest.fixture
def test_fii(db_session: Session, test_user: User):
    """
    Create test FII.

    Returns:
        Fii: Test FII with realistic Brazilian data
    """
    fii = Fii(
        tag=fake.lexify(text="????11").upper(),  # e.g., "XPLG11"
        name=fake.company() + " FII",
        sector="Logística",
        created_by_pk=test_user.pk,
        updated_by_pk=test_user.pk,
    )

    db_session.add(fii)
    db_session.commit()
    db_session.refresh(fii)

    return fii


@pytest.fixture
def another_test_fii(db_session: Session, test_user: User):
    """
    Create second test FII for multi-FII tests.

    Returns:
        Fii: Another test FII
    """
    fii = Fii(
        tag=fake.lexify(text="????11").upper(),
        name=fake.company() + " FII",
        sector="Shopping",
        created_by_pk=test_user.pk,
        updated_by_pk=test_user.pk,
    )

    db_session.add(fii)
    db_session.commit()
    db_session.refresh(fii)

    return fii


@pytest.fixture
def deleted_test_fii(db_session: Session, test_user: User):
    """
    Create soft-deleted test FII.

    Returns:
        Fii: Soft-deleted FII with rm_timestamp set
    """
    import time

    fii = Fii(
        tag=fake.lexify(text="????11").upper(),
        name=fake.company() + " FII (DELETED)",
        sector="Lajes Corporativas",
        created_by_pk=test_user.pk,
        updated_by_pk=test_user.pk,
        rm_timestamp=int(time.time()),
    )

    db_session.add(fii)
    db_session.commit()
    db_session.refresh(fii)

    return fii


@pytest.fixture
def multiple_test_fiis(db_session: Session, test_user: User):
    """
    Create multiple test FIIs for pagination tests.

    Returns:
        list[Fii]: List of 10 test FIIs
    """
    fiis = []
    sectors = ["Logística", "Shopping", "Lajes Corporativas", "Títulos e Val. Mob.", "Híbrido"]

    for i in range(10):
        fii = Fii(
            tag=fake.lexify(text="????11").upper(),
            name=f"{fake.company()} FII {i+1}",
            sector=sectors[i % len(sectors)],
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        fiis.append(fii)

    db_session.add_all(fiis)
    db_session.commit()

    for fii in fiis:
        db_session.refresh(fii)

    return fiis


@pytest.fixture
def fiis_multiple_sectors(db_session: Session, test_user: User):
    """
    Create FIIs across multiple sectors for filtering tests.

    Returns:
        dict: {"logistica": [Fii], "shopping": [Fii], "lajes": [Fii]}
    """
    fiis = {
        "logistica": [],
        "shopping": [],
        "lajes": [],
    }

    # Create 2 FIIs per sector
    for _ in range(2):
        fii_logistica = Fii(
            tag=fake.lexify(text="????11").upper(),
            name=fake.company() + " Logística FII",
            sector="Logística",
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        fiis["logistica"].append(fii_logistica)

        fii_shopping = Fii(
            tag=fake.lexify(text="????11").upper(),
            name=fake.company() + " Shopping FII",
            sector="Shopping",
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        fiis["shopping"].append(fii_shopping)

        fii_lajes = Fii(
            tag=fake.lexify(text="????11").upper(),
            name=fake.company() + " Lajes FII",
            sector="Lajes Corporativas",
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        fiis["lajes"].append(fii_lajes)

    all_fiis = fiis["logistica"] + fiis["shopping"] + fiis["lajes"]
    db_session.add_all(all_fiis)
    db_session.commit()

    for fii_list in fiis.values():
        for fii in fii_list:
            db_session.refresh(fii)

    return fiis


# ============================================================================
# TRANSACTION FIXTURES
# ============================================================================

@pytest.fixture
def test_transaction(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create test buy transaction.

    Returns:
        FiiTransaction: Buy transaction
    """
    transaction = FiiTransaction(
        user_pk=test_user.pk,
        fii_pk=test_fii.pk,
        transaction_type="buy",
        transaction_date=date.today() - timedelta(days=30),
        quantity=100,
        price_per_unit=Decimal("95.50"),
        total_amount=Decimal("9550.00"),
        created_by_pk=test_user.pk,
        updated_by_pk=test_user.pk,
    )

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    return transaction


@pytest.fixture
def other_user_transaction(db_session: Session, another_test_user: User, test_fii: Fii):
    """
    Create transaction owned by another user for ownership tests.

    Returns:
        FiiTransaction: Transaction owned by another_test_user
    """
    transaction = FiiTransaction(
        user_pk=another_test_user.pk,
        fii_pk=test_fii.pk,
        transaction_type="buy",
        transaction_date=date.today() - timedelta(days=15),
        quantity=50,
        price_per_unit=Decimal("100.00"),
        total_amount=Decimal("5000.00"),
        created_by_pk=another_test_user.pk,
        updated_by_pk=another_test_user.pk,
    )

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    return transaction


@pytest.fixture
def buy_and_sell_transactions(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create both buy and sell transactions for type filtering tests.

    Returns:
        dict: {"buy": [FiiTransaction], "sell": [FiiTransaction]}
    """
    transactions = {"buy": [], "sell": []}

    # Create 2 buy transactions
    for i in range(2):
        buy_transaction = FiiTransaction(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            transaction_type="buy",
            transaction_date=date.today() - timedelta(days=60 - i*10),
            quantity=100 + i*50,
            price_per_unit=Decimal("95.00") + Decimal(i),
            total_amount=Decimal((100 + i*50) * (95.00 + i)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        transactions["buy"].append(buy_transaction)

    # Create 2 sell transactions
    for i in range(2):
        sell_transaction = FiiTransaction(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            transaction_type="sell",
            transaction_date=date.today() - timedelta(days=20 - i*5),
            quantity=50 + i*20,
            price_per_unit=Decimal("100.00") + Decimal(i*2),
            total_amount=Decimal((50 + i*20) * (100.00 + i*2)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        transactions["sell"].append(sell_transaction)

    all_transactions = transactions["buy"] + transactions["sell"]
    db_session.add_all(all_transactions)
    db_session.commit()

    for trans_list in transactions.values():
        for trans in trans_list:
            db_session.refresh(trans)

    return transactions


@pytest.fixture
def transactions_multiple_fiis(db_session: Session, test_user: User, test_fii: Fii, another_test_fii: Fii):
    """
    Create transactions for multiple FIIs for filtering tests.

    Returns:
        dict: {test_fii.pk: [FiiTransaction], another_test_fii.pk: [FiiTransaction]}
    """
    transactions = {test_fii.pk: [], another_test_fii.pk: []}

    # Create 2 transactions for each FII
    for fii in [test_fii, another_test_fii]:
        for i in range(2):
            transaction = FiiTransaction(
                user_pk=test_user.pk,
                fii_pk=fii.pk,
                transaction_type="buy",
                transaction_date=date.today() - timedelta(days=30 - i*10),
                quantity=100,
                price_per_unit=Decimal("95.00"),
                total_amount=Decimal("9500.00"),
                created_by_pk=test_user.pk,
                updated_by_pk=test_user.pk,
            )
            transactions[fii.pk].append(transaction)

    all_transactions = transactions[test_fii.pk] + transactions[another_test_fii.pk]
    db_session.add_all(all_transactions)
    db_session.commit()

    for trans_list in transactions.values():
        for trans in trans_list:
            db_session.refresh(trans)

    return transactions


@pytest.fixture
def transactions_various_dates(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create transactions across various dates for date range filtering.

    Returns:
        list[FiiTransaction]: Transactions from 90 days ago to today
    """
    transactions = []

    # Create transactions at 10-day intervals over 90 days
    for i in range(10):
        transaction = FiiTransaction(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            transaction_type="buy",
            transaction_date=date.today() - timedelta(days=90 - i*10),
            quantity=100,
            price_per_unit=Decimal("95.00") + Decimal(i),
            total_amount=Decimal(100 * (95.00 + i)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        transactions.append(transaction)

    db_session.add_all(transactions)
    db_session.commit()

    for trans in transactions:
        db_session.refresh(trans)

    return transactions


@pytest.fixture
def many_transactions(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create many transactions for pagination tests.

    Returns:
        list[FiiTransaction]: 15 transactions
    """
    transactions = []

    for i in range(15):
        transaction = FiiTransaction(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            transaction_type="buy" if i % 2 == 0 else "sell",
            transaction_date=date.today() - timedelta(days=100 - i*5),
            quantity=100,
            price_per_unit=Decimal("95.00") + Decimal(i),
            total_amount=Decimal(100 * (95.00 + i)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        transactions.append(transaction)

    db_session.add_all(transactions)
    db_session.commit()

    for trans in transactions:
        db_session.refresh(trans)

    return transactions


# ============================================================================
# DIVIDEND FIXTURES
# ============================================================================

@pytest.fixture
def test_dividend(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create test dividend.

    Returns:
        Dividend: Test dividend payment
    """
    dividend = Dividend(
        user_pk=test_user.pk,
        fii_pk=test_fii.pk,
        payment_date=date.today() - timedelta(days=15),
        reference_date=date.today() - timedelta(days=30),
        amount_per_unit=Decimal("0.85"),
        units_held=100,
        total_amount=Decimal("85.00"),
        created_by_pk=test_user.pk,
        updated_by_pk=test_user.pk,
    )

    db_session.add(dividend)
    db_session.commit()
    db_session.refresh(dividend)

    return dividend


@pytest.fixture
def other_user_dividend(db_session: Session, another_test_user: User, test_fii: Fii):
    """
    Create dividend owned by another user for ownership tests.

    Returns:
        Dividend: Dividend owned by another_test_user
    """
    dividend = Dividend(
        user_pk=another_test_user.pk,
        fii_pk=test_fii.pk,
        payment_date=date.today() - timedelta(days=10),
        reference_date=date.today() - timedelta(days=25),
        amount_per_unit=Decimal("0.90"),
        units_held=50,
        total_amount=Decimal("45.00"),
        created_by_pk=another_test_user.pk,
        updated_by_pk=another_test_user.pk,
    )

    db_session.add(dividend)
    db_session.commit()
    db_session.refresh(dividend)

    return dividend


@pytest.fixture
def dividends_multiple_fiis(db_session: Session, test_user: User, test_fii: Fii, another_test_fii: Fii):
    """
    Create dividends for multiple FIIs for filtering tests.

    Returns:
        dict: {test_fii.pk: [Dividend], another_test_fii.pk: [Dividend]}
    """
    dividends = {test_fii.pk: [], another_test_fii.pk: []}

    # Create 2 dividends for each FII
    for fii in [test_fii, another_test_fii]:
        for i in range(2):
            dividend = Dividend(
                user_pk=test_user.pk,
                fii_pk=fii.pk,
                payment_date=date.today() - timedelta(days=15 + i*30),
                reference_date=date.today() - timedelta(days=30 + i*30),
                amount_per_unit=Decimal("0.85") + Decimal(i) * Decimal("0.05"),
                units_held=100,
                total_amount=Decimal(100 * (0.85 + i * 0.05)),
                created_by_pk=test_user.pk,
                updated_by_pk=test_user.pk,
            )
            dividends[fii.pk].append(dividend)

    all_dividends = dividends[test_fii.pk] + dividends[another_test_fii.pk]
    db_session.add_all(all_dividends)
    db_session.commit()

    for div_list in dividends.values():
        for div in div_list:
            db_session.refresh(div)

    return dividends


@pytest.fixture
def dividends_various_dates(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create dividends across various dates for date range filtering.

    Returns:
        list[Dividend]: Dividends from 120 days ago to today
    """
    dividends = []

    # Create monthly dividends over 4 months
    for i in range(4):
        dividend = Dividend(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            payment_date=date.today() - timedelta(days=15 + i*30),
            reference_date=date.today() - timedelta(days=30 + i*30),
            amount_per_unit=Decimal("0.80") + Decimal(i) * Decimal("0.05"),
            units_held=100,
            total_amount=Decimal(100 * (0.80 + i * 0.05)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        dividends.append(dividend)

    db_session.add_all(dividends)
    db_session.commit()

    for div in dividends:
        db_session.refresh(div)

    return dividends


@pytest.fixture
def many_dividends(db_session: Session, test_user: User, test_fii: Fii):
    """
    Create many dividends for pagination tests.

    Returns:
        list[Dividend]: 12 monthly dividends
    """
    dividends = []

    for i in range(12):
        dividend = Dividend(
            user_pk=test_user.pk,
            fii_pk=test_fii.pk,
            payment_date=date.today() - timedelta(days=15 + i*30),
            reference_date=date.today() - timedelta(days=30 + i*30),
            amount_per_unit=Decimal("0.80") + Decimal(i % 4) * Decimal("0.05"),
            units_held=100,
            total_amount=Decimal(100 * (0.80 + (i % 4) * 0.05)),
            created_by_pk=test_user.pk,
            updated_by_pk=test_user.pk,
        )
        dividends.append(dividend)

    db_session.add_all(dividends)
    db_session.commit()

    for div in dividends:
        db_session.refresh(div)

    return dividends


# ============================================================================
# REFRESH TOKEN FIXTURES
# ============================================================================

@pytest.fixture
def test_user_refresh_token(db_session: Session, test_user: User):
    """
    Create refresh token for test user.

    Returns:
        RefreshToken: Valid refresh token
    """
    from datetime import datetime, timedelta, timezone
    from app.core.security import create_refresh_token

    token_str = create_refresh_token(data={"sub": str(test_user.pk)})
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    refresh_token = RefreshToken(
        user_pk=test_user.pk,
        token=token_str,
        expires_at=expires_at,
        device_info="pytest",
    )

    db_session.add(refresh_token)
    db_session.commit()
    db_session.refresh(refresh_token)

    # Store token string for use in tests
    refresh_token.token_str = token_str  # type: ignore

    return refresh_token
