from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.sql import func


class PsqlTimestampsMixin:
    created_at = Column(
        "created_at", TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        index=True,
        unique=False,
        server_default=func.now(),
        onupdate=func.now()
    )
