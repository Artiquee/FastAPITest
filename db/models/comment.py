from sqlalchemy import Column, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.db_settings import Base
from db.mixins import psql_timestamps_mixin, psql_primary_key_mixin


class Comment(
    Base,
    psql_primary_key_mixin.PsqlPrimaryKeyMixin,
    psql_timestamps_mixin.PsqlTimestampsMixin,
):
    __tablename__ = 'comments'
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    is_blocked = Column(Boolean, nullable=False, server_default='false')
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
