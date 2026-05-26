"""
🦄 Main.py - CONTROLLER (Endpoints)

AGREGAR ESTOS IMPORTS AL main.py EXISTENTE:

from models import User, UserReview
from database import get_db
from auth import hash_password, verify_password, create_access_token, verify_token
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import os

---

AGREGAR ESTOS MODELOS:

class UserRegister(BaseModel):
    email: str
    password: str

class UserFeedback(BaseModel):
    book_title: str
    review_text: str
    rating: int

---

AGREGAR ESTE MIDDLEWARE:

def get_current_user(authorization: str = Header(..., alias="Authorization")) -> str:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid scheme")
        email = verify_token(token)
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

---

AGREGAR ESTOS ENDPOINTS:
"""

# XXX TODO: COPIAR LOS IMPORTS DE ARRIBA AL MAIN.py EXISTENTE

# ============================================
# ENDPOINTS AUTENTICACIÓN
# ============================================

# @app.post("/auth/register")
# def register(user: UserRegister, db: Session = Depends(get_db)):
#     """
#     Registra un usuario nuevo.
#     XXX TODO: Implementar:
#     1. Verificar que email no existe
#     2. Hash de contraseña
#     3. Crear User
#     4. db.add + db.commit
#     5. Generar JWT
#     6. Retornar token
#     """
#     pass


# @app.post("/auth/login")
# def login(user: UserRegister, db: Session = Depends(get_db)):
#     """
#     Loquea un usuario existente.
#     XXX TODO: Implementar:
#     1. Buscar User por email
#     2. verify_password
#     3. Si OK, generar JWT
#     4. Retornar token
#     """
#     pass


# ============================================
# ENDPOINTS USUARIO
# ============================================

# @app.get("/user/me")
# def get_me(current_user: str = Depends(get_current_user)):
#     """
#     Retorna info del usuario actual (autenticado).
#     """
#     return {"email": current_user}


# @app.post("/user/feedback")
# def save_feedback(
#     feedback: UserFeedback,
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Guarda una review de un usuario (RETROALIMENTACIÓN).
#     XXX TODO: Implementar:
#     1. Crear UserReview con datos del feedback
#     2. user_email = current_user
#     3. created_at = datetime.utcnow()
#     4. db.add + db.commit
#     5. Retornar {"status": "saved", "review_id": ...}
#     """
#     pass


# @app.get("/user/history")
# def get_history(
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Retorna historial de reviews del usuario.
#     """
#     reviews = db.query(UserReview).filter(UserReview.user_email == current_user).all()
#     return {
#         "email": current_user,
#         "reviews": [
#             {
#                 "book_title": r.book_title,
#                 "review_text": r.review_text,
#                 "rating": r.rating,
#                 "created_at": r.created_at.isoformat()
#             }
#             for r in reviews
#         ]
#     }

print("✅ Copiar estos endpoints al main.py existente")
