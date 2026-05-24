# 🦄 Feature: JWT Auth + Retroalimentación

**Rama:** `feature-jwt-auth`  
**Objetivo:** Agregar autenticación JWT + sistema de retroalimentación de usuarios

---

## ¿Qué Es Esta Rama?

Un scaffold (esqueleto) con toda la estructura necesaria para implementar:
- ✅ JWT authentication (login/register seguro)
- ✅ Retroalimentación: usuarios dejan reviews de libros
- ✅ Crowdsourcing: usuarios agregan libros nuevos + reviews
- ✅ Base de datos: PostgreSQL con SQLAlchemy ORM

Contiene código base ya estructurado, documentación clara, y puntos específicos (`XXX TODO`) para que implementes la lógica. No es un proyecto completo: es una **guía de referencia** que puedes usar, explorar y adaptar a tu proyecto.

---

## 📦 Qué Encontrarás Aquí

### 📚 Documentación (carpeta `docs/`)
- **MVC_EXPLICADO.md** - Explica la arquitectura Model-View-Controller y cómo se aplica a este proyecto
- **JWT_SETUP.md** - Guía paso a paso de implementación con ejemplos de código
- **STRUCTURE_ALIGNMENT.md** - Cómo se alinean los datos del CSV original con las nuevas tablas de base de datos
- **DEPLOY_RENDER.md** - Instrucciones para desplegar la aplicación en producción

### 🔧 Backend Python (carpeta `backend/`)
- **models.py** - Definiciones SQLAlchemy de las tablas (User, UserReview, NewBook, NewBookReview). Marca con `XXX TODO` dónde implementar
- **database.py** - Configuración de PostgreSQL y conexión. Con `XXX TODO` para completar
- **auth.py** - Funciones de seguridad: hash de contraseñas, creación de JWT, validación. Con `XXX TODO`
- **schemas.py** - Validación de datos con Pydantic (ya completo)
- **main.py** - Endpoints de la API comentados. Copiar/implementar los `XXX TODO`
- **requirements.txt** - Dependencias Python (sqlalchemy, fastapi, python-jose, passlib, etc.)
- **tests/test_auth.py** - Tests unitarios que te guían en qué implementar
- **.env.example** - Template de variables de entorno

### 🎨 Frontend React (carpeta `frontend/src/components/`)

Dos componentes principales para aprender:

**`Auth/`** - Autenticación (login/register)
```
Auth/
├── Login/
│   ├── Login.jsx          ← Componente de formulario
│   ├── Login.module.css   ← Estilos BEM
│   └── README.md
```

**`Feedback/`** - Retroalimentación (reviews de libros)
```
Feedback/
├── FeedbackForm/
│   ├── FeedbackForm.jsx   ← Ejemplo de reutilización del patrón
│   ├── FeedbackForm.module.css
│   └── README.md
```

**Patrón:** Cada componente en su carpeta con JSX, CSS (BEM) y README

### 🐳 Infrastructure
- **docker-compose.yml** - Levanta PostgreSQL automáticamente
- **.gitignore** - Qué no commitear

---

## 🎯 Cómo Usar Esta Rama

---

## 🚨 ¿Tienes Un Proyecto Existente?

**Si ya tienes código en `equipo-1-libros` o `equipo-2-libros`:**

Lee **INTEGRACIÓN.md** PRIMERO. Te explica cómo agregar esto sin romper nada.

No hagas merge directo. Sigue los pasos en INTEGRACIÓN.md para copiar selectivamente.

---

## Cómo Empezar

### ✅ Primero: Verificación
Antes de cualquier cosa, asegúrate que tienes todo instalado y configurado:

📋 **Lee `VERIFICACIÓN.md`** (5 minutos)

Este archivo te guía a través de checks para confirmar:
- Python, Node.js, Docker instalados
- Archivos en la estructura correcta
- Dependencias instaladas
- Backend y Frontend levantan sin errores

**NO sigas adelante si algo falla en VERIFICACIÓN.md**

---

### 1. Setup Local

```bash
cd backend
pip install -r requirements.txt

cd ..
cp .env.example .env
# Editar .env: generar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

docker-compose up
# Esperar: "database system is ready"
```

### 2. Leer Documentación

1. **PRIMERO:** `docs/MVC_EXPLICADO.md` - Entiende la arquitectura
2. **SEGUNDO:** `docs/JWT_SETUP.md` - Implementación paso a paso
3. **TERCERO:** `docs/STRUCTURE_ALIGNMENT.md` - Cómo se alinean los datos

### 3. Implementar

Busca todos los `# XXX TODO:` en:
- `backend/models.py` (8 campos SQLAlchemy)
- `backend/database.py` (4 funciones)
- `backend/auth.py` (4 funciones)
- `backend/main.py` (5 endpoints)
- `frontend/src/components/Login.jsx` (componente)

Cada `# XXX TODO:` tiene un comentario explicando exactamente qué implementar.

### 4. Test

```bash
# Tests unitarios
python -m pytest backend/tests/test_auth.py -v

# Manual: levantar servicios
docker-compose up       # Terminal 1
npm start              # Terminal 2 (frontend)
python -m uvicorn backend.main:app --reload  # Terminal 3

# Navegador: http://localhost:3000
# Registra, busca un libro, deja una review
```

---

## 📁 Estructura

```
├── docs/
│   ├── MVC_EXPLICADO.md              ← Entiende la arquitectura
│   ├── JWT_SETUP.md                  ← Guía paso a paso de implementación
│   ├── FORMULARIOS_GUIA.md           ← Cómo hacer formularios React
│   ├── FRONTEND_PROFESIONAL.md       ← Por qué el UI/UX importa
│   ├── STRUCTURE_ALIGNMENT.md        ← Cómo alinean datos CSV con BD
│   └── DEPLOY_RENDER.md              ← Deploy a producción (opcional)
├── backend/
│   ├── models.py                     ← XXX TODO: Tablas SQLAlchemy
│   ├── database.py                   ← XXX TODO: Conexión PostgreSQL
│   ├── auth.py                       ← XXX TODO: Hash + JWT
│   ├── schemas.py                    ← Validación Pydantic (listo)
│   ├── main.py                       ← XXX TODO: Endpoints API
│   ├── requirements.txt               ← Dependencias Python
│   ├── .env.example                  ← Plantilla de variables
│   └── tests/test_auth.py            ← Tests unitarios
├── frontend/src/components/
│   ├── Auth/
│   │   └── Login/
│   │       ├── Login.jsx
│   │       ├── Login.module.css
│   │       └── README.md
│   └── Feedback/
│       └── FeedbackForm/
│           ├── FeedbackForm.jsx
│           ├── FeedbackForm.module.css
│           └── README.md
├── docker-compose.yml                ← PostgreSQL service
├── README.md                          ← Este archivo
├── INTEGRACIÓN.md                     ← Cómo integrar sin romper nada
└── PARA_LOS_EQUIPOS.md               ← Sobre optionalidad del scaffold

```

---

## 🔍 Dónde Hay Puntos para Implementar

### Backend: Busca `# XXX TODO:`

| Archivo | Puntos TODO | Para Qué |
|---------|-------------|----------|
| `backend/models.py` | 8 | Definir campos de tablas SQLAlchemy |
| `backend/database.py` | 5 | Conectar PostgreSQL y crear sesiones |
| `backend/auth.py` | 4 | Funciones de hash y JWT |
| `backend/main.py` | 5 | Endpoints de API (register, login, feedback) |

### Frontend: Aprende Formularios React

Si **nunca** has hecho un formulario React:

1. **Lee primero:** `docs/FORMULARIOS_GUIA.md` (20 minutos)
   - Explica `useState`, `onChange`, `onSubmit` desde cero
   - Enseña cómo enviar datos al backend
   - Muestra cómo guardar tokens en `localStorage`

2. **Después, mira:** `frontend/src/components/Auth/Login/Login.jsx`
   - El patrón real, aplicado
   - Comentarios explicando cada parte importante
   - Cómo enviar token en headers para requests autenticados

3. **Practica igual:** `frontend/src/components/Feedback/FeedbackForm/FeedbackForm.jsx`
   - Mismo patrón de formulario, diferente contexto
   - Demuestra que el patrón es reutilizable

---

## 📚 Documentación Incluida

| Archivo | Para Qué |
|---------|----------|
| `docs/MVC_EXPLICADO.md` | Entiende la arquitectura (qué es cada capa) |
| `docs/JWT_SETUP.md` | Cómo implementar cada parte (paso a paso) |
| `docs/FORMULARIOS_GUIA.md` | **← Si NUNCA has hecho formularios React, LEE ESTO PRIMERO** |
| `docs/FRONTEND_PROFESIONAL.md` | Frontend que se ve serio (cuando empresas revisen) |
| `docs/STRUCTURE_ALIGNMENT.md` | Cómo alinean los datos CSV con las nuevas tablas |
| `docs/DEPLOY_RENDER.md` | Cómo hacer deploy a producción |

---

## 🔄 Ejemplo: Flujo de Usuario

```
1. Usuario accede a http://localhost:3000
   ↓
2. Se registra/logea
   ↓ (backend: bcrypt + JWT token)
   ↓
3. Busca un libro
   ↓ (frontend envía token, backend verifica autenticación)
   ↓
4. Deja una review
   ↓ (backend guarda en base de datos)
   ↓
5. Busca un libro que no existe
   ↓ (opción: agregarlo con su reseña)
   ↓
6. Próximo usuario encuentra ese libro
   ↓ (con reviews que mejoran el análisis de sentimientos)
```

---

## 🐛 Errores Comunes

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: sqlalchemy` | `pip install -r requirements.txt` |
| `Connection refused (postgres)` | `docker-compose up` (espera "database system is ready") |
| `JWT invalid` | Frontend debe enviar: `Authorization: Bearer <token>` en headers |
| `CORS error` | Backend CORS config (ver `main.py`) |
| `Email already registered` | Normal, usar otro email |

---

## 📊 Opcionales (Sección 5.5 en JWT_SETUP.md)

Si quieres ir más allá:
- [ ] Endpoint POST `/book/add-with-review` (agregar libros nuevos)
- [ ] Validación: usuario no agrega duplicados
- [ ] Sentiment analyzer lee nuevas reviews
- [ ] Recomendaciones mejoran con datos nuevos

---

## 📦 Deploy a Producción

Ver `docs/DEPLOY_RENDER.md` para:
- Crear PostgreSQL en Render (gratis)
- Desplegar backend (FastAPI)
- Desplegar frontend (React)
- Testear en vivo

---

## 💡 Tips

- **Usa los XXX TODO como guía:** Cada uno tiene un comentario claro
- **Lee MVC_EXPLICADO primero:** Sin entender arquitectura, los XXX TODO no tienen sentido
- **Tests te guían:** `pytest backend/tests/test_auth.py` muestra qué falta
- **Debugging:** `docker-compose logs postgres` si hay problemas de BD

---

## 🦄 Del Unicornio

> Esta rama es un punto de partida. Algunos copiarán exacto. Otros modificarán.  
> Lo importante es entender **por qué** cada pa