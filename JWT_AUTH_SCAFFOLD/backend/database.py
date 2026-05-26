"""
🦄 DATABASE - Conexión a PostgreSQL

Inicializa tablas, crea sesiones.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# XXX TODO: DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dev:dev@postgres:5432/book_recommendations")
DATABASE_URL = None

# XXX TODO: engine = create_engine(DATABASE_URL)
engine = None

# XXX TODO: SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = None

# XXX TODO: Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency injection para FastAPI"""
    # XXX TODO:
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    pass
