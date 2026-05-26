"""
🦄 Tests para Auth

XXX TODO: Estos tests FALLAN intencionalmente hasta que implementen auth.py

Correr: python -m pytest tests/test_auth.py -v

La idea es: implementar funciones hasta que todos los tests pasen (TDD).
"""

import pytest
from auth import hash_password, verify_password, create_access_token, verify_token


# ============================================
# TESTS HASHING
# ============================================

def test_hash_password():
    """XXX TODO: Debe pasar cuando implementen hash_password()"""
    password = "testpassword123"
    hashed = hash_password(password)

    # La contraseña hasheada NO debe ser igual a la original
    assert hashed != password

    # Pero debe empezar con $2b$ (bcrypt signature)
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """XXX TODO: verify_password debe retornar True si coinciden"""
    password = "testpassword123"
    hashed = hash_password(password)

    # Verificar que coinciden
    assert verify_password(password, hashed) == True


def test_verify_password_incorrect():
    """XXX TODO: verify_password debe retornar False si no coinciden"""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)

    # Verificar que NO coinciden
    assert verify_password(wrong_password, hashed) == False


# ============================================
# TESTS JWT
# ============================================

def test_create_access_token():
    """XXX TODO: Debe crear un token válido"""
    data = {"sub": "alumno@test.com"}
    token = create_access_token(data)

    # El token no debe ser None
    assert token is not None

    # El token debe ser string
    assert isinstance(token, str)

    # JWT tiene 3 partes separadas por puntos
    assert token.count(".") == 2


def test_verify_token_valid():
    """XXX TODO: Debe extraer email del token válido"""
    email = "alumno@test.com"
    data = {"sub": email}
    token = create_access_token(data)

    # Verificar token debe retornar el email
    extracted_email = verify_token(token)
    assert extracted_email == email


def test_verify_token_invalid():
    """XXX TODO: Debe retornar None si token es inválido"""
    invalid_token = "invalid.token.here"

    # Verificar token inválido debe retornar None
    result = verify_token(invalid_token)
    assert result is None


def test_verify_token_tampered():
    """XXX TODO: Debe detectar si token fue modificado"""
    email = "alumno@test.com"
    data = {"sub": email}
    token = create_access_token(data)

    # Modificar el token (borrar último carácter)
    tampered_token = token[:-1] + "X"

    # Debe fallar la verificación
    result = verify_token(tampered_token)
    assert result is None


# ============================================
# INTEGRACIÓN
# ============================================

def test_full_auth_flow():
    """XXX TODO: Test completo: hash -> verify -> token -> verify token"""

    # 1. Usuario se registra con contraseña
    password = "mysecurepassword123"
    hashed = hash_password(password)

    # 2. Usuario intenta loguear con contraseña correcta
    assert verify_password(password, hashed) == True

    # 3. Backend crea JWT
    email = "alumno@test.com"
    token = create_access_token({"sub": email})
    assert token is not None

    # 4. Usuario envía token en siguiente request
    # 5. Backend verifica token
    verified_email = verify_token(token)
    assert verified_email == email


# ============================================
# NOTAS DEL UNICORNIO
# ============================================

"""
¿Cómo correr los tests?

1. Terminal:
   cd backend
   pytest tests/test_auth.py -v

2. Resultado esperado ANTES de implementar:
   FAILED - porque las funciones retornan pass (None)

3. Después de implementar:
   PASSED - todos los tests verdes ✅

4. TDD = Test-Driven Development
   Es decir: escribe tests primero, implementa después para que pasen.

   Beneficio: sabes exactamente qué debe hacer el código.

🦄
"""
