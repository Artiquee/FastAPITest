from sqlalchemy import Column, Text, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.db_settings import Base
from db.mixins import psql_timestamps_mixin, psql_primary_key_mixin


class Post(
    Base,
    psql_primary_key_mixin.PsqlPrimaryKeyMixin,
    psql_timestamps_mixin.PsqlTimestampsMixin,
):
    __tablename__ = 'posts'
    title = Column(String, index=True)
    content = Column(Text)
    autoreply = Column(Boolean, default=False)
    autoreply_delay = Column(Integer, default=0)
    autoreply_msg = Column(Text, default="")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
