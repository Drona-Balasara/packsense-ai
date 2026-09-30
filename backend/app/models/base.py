"""
Shared SQLAlchemy declarative base.
Import Base from here in every model file so all tables share one metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
