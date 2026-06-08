from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Provides modern type hinting support and metaclass configurations.
    """
    pass
