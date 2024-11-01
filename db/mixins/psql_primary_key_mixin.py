from sqlalchemy import Column, BigInteger


class PsqlPrimaryKeyMixin:
    id = Column("id", BigInteger, primary_key=True, autoincrement=True)
