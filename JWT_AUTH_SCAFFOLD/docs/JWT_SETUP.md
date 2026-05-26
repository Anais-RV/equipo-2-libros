# 🦄 JWT Setup - Paso a Paso

**Objetivo:** Implementar autenticación + retroalimentación en 9 días.

---

## 0. Antes de Empezar

Lee: `MVC_EXPLICADO.md` → entiende la arquitectura

### Setup Local

```bash
cd backend

# 1. Instalar librerías nuevas en requirements.txt:
# - sqlalchemy==2.0.27
# - python-jose[cryptography]==3.3.0
# - passlib[bcrypt]==1.7.4

pip install -r requirements.txt

# 2. Crear .env
cp .env.example .env
# Generar SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"

# 3. Iniciar PostgreSQL
cd ..
docker-compose up
# Esperar logs: "postgres_1  | 2026-05-19 10:00:00.000 UTC [1] LOG: database system is ready"
```

---

## 1. Implementar Models (1 hora)

**Archivo:** `backend/models.py`

Reemplacer los `# XXX TODO:` con las columnas SQLAlchemy.

---

## 2. Implementar Database (30 min)

**Archivo:** `backend/database.py`

Conectar a PostgreSQL y crear sesiones.

---

## 3. Implementar Auth (1.5 horas)

**Archivo:** `backend/auth.py`

Implementar funciones de hash y JWT.

---

## 4. Actualizar Main.py (2 horas)

Agregar endpoints de registro, login, y retroalimentación.

---

## 5. Implementar Frontend (1.5 horas)

**Archivo:** `frontend/src/components/Auth/Login/Login.jsx`

Ver el archivo actual - tiene comentarios pedagógicos.

---

## 6. Testing Local (1 hora)

```bash
# Terminal 1
docker-compose up

# Terminal 2
cd frontend
npm start

# Navegador: http://localhost:3000
```

---

## 7. Checklist Final

- [ ] Models implementado
- [ ] Database conecta
- [ ] Auth funciona
- [ ] Main.py tiene endpoints
- [ ] Login.jsx funciona
- [ ] docker-compose levanta todo

---

> Del unicornio. Adelante. 🦄
