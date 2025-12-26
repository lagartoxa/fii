"""
ImportJob model - CSV/Excel file import tracking with error details.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User


class ImportJob(BaseModel):
    """
    ImportJob model for tracking file import operations.

    Table: import_job (SINGULAR)

    Purpose: Track CSV/Excel file imports with error details.

    Error Details Format (JSONB):
    {
      "errors": [
        {"row": 5, "field": "ticker", "message": "Invalid ticker", "value": "INVALID"},
        {"row": 12, "field": "date", "message": "Invalid date format", "value": "2024-13-45"}
      ]
    }

    Relationships:
    - Many-to-one → User (user who created this import job)

    RLS: Enabled - users can only access their own import jobs
    """

    __tablename__ = "import_job"
    __table_args__ = (
        CheckConstraint(
            "import_type IN ('transaction', 'dividend')",
            name='ck_import_job_type'
        ),
        {'comment': 'CSV/Excel file import tracking with error details'}
    )

    user_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('user.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Owner user reference"
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original file name"
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )

    import_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Import type: 'transaction' or 'dividend'"
    )

    error_details: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Row-level error details in JSON format"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="import_jobs",
        foreign_keys=[user_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<ImportJob(pk={self.pk}, file_name='{self.file_name}', "
            f"type='{self.import_type}')>"
        )
