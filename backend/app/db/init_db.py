from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_db(db: Session) -> None:
    """
    Initialize database with default data.

    This function creates the default admin user.
    Note: Database tables should be created via Alembic migrations.
    Run 'alembic upgrade head' before calling this function.
    """
    # Import all models to ensure they are registered
    from app.db.models import user, fii, fii_transaction, dividend

    # Create default admin user (if needed)
    from app.db.models.user import User
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrator",
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        logger.info("✓ Default admin user created (username: admin)")
    else:
        logger.info("✓ Admin user already exists")
