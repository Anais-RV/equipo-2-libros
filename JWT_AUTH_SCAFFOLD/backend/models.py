"""
🦄 MODELS - Las Tablas de la Base de Datos

Aquí definimos:
- User: quién se loquea
- UserReview: reviews de libros EXISTENTES (retroalimentación)
- NewBook: libros NUEVOS que aportan usuarios (crowdsourcing)
- NewBookReview: reviews de esos libros nuevos

SQLAlchemy convierte esto a SQL automáticamente.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Tabla: users - Quién se loquea"""

    __tablename__ = "users"

    # XXX TODO: email = Column(String, primary_key=True, unique=True, nullable=False)
    email = None

    # XXX TODO: password_hash = Column(String, nullable=False)
    password_hash = None

    # XXX TODO: created_at = Column(DateTime, default=datetime.utcnow)
    created_at = None

    def __repr__(self):
        return f"<User(email={self.email})>"


class UserReview(Base):
    """
    Tabla: user_reviews

    Reviews de libros EXISTENTES (en el dataset original).
    Estos datos retroalimentan el modelo.
    """

    __tablename__ = "user_reviews"

    # XXX TODO: id = Column(Integer, primary_key=True, autoincrement=True)
    id = None

    # XXX TODO: user_email = Column(String, ForeignKey("users.email"), nullable=False)
    user_email = None

    # XXX TODO: book_title = Column(String, nullable=False)
    book_title = None

    # XXX TODO: review_text = Column(Text, nullable=False)
    review_text = None

    # XXX TODO: rating = Column(Integer, nullable=False)
    rating = None

    # XXX TOD