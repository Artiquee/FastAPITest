from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from db.db_settings import Base
from db.mixins import psql_primary_key_mixin, psql_timestamps_mixin


class User(
    Base,
    psql_primary_key_mixin.PsqlPrimaryKeyMixin,
    psql_timestamps_mixin.PsqlTimestampsMixin,
):
    __tablename__ = 'users'
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="author")
