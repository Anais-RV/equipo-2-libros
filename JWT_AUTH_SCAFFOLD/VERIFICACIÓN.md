# ✅ Checklist de Verificación

Usa esta lista para confirmar que el scaffold está listo antes de empezar a implementar.

---

## 1. Antes de Empezar: Requisitos

- [ ] Python 3.8+ instalado → `python --version`
- [ ] Node.js + npm → `node --version` y `npm --version`
- [ ] Docker instalado → `docker --version`
- [ ] Git instalado → `git --version`
- [ ] Editor de código (VS Code recomendado)

---

## 2. Repositorio Clonado / Rama Copiada

En tu máquina, deberías tener:

```
mi-proyecto/
├── docs/
│   ├── MVC_EXPLICADO.md
│   ├── JWT_SETUP.md
│   ├── FORMULARIOS_GUIA.md
│   ├── FRONTEND_PROFESIONAL.md
│   ├── STRUCTURE_ALIGNMENT.md
│   └── DEPLOY_RENDER.md
├── backend/
│   ├── models.py           ← Con XXX TODO
│   ├── database.py         ← Con XXX TODO
│   ├── auth.py             ← Con XXX TODO
│   ├── schemas.py
│   ├── main.py             ← Con XXX TODO
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/test_auth.py
├── frontend/src/components/
│   ├── Auth/Login/
│   │   ├── Login.jsx
│   │   ├── Login.module.css
│   │   └── README.md
│   └── Feedback/FeedbackForm/
│       ├── FeedbackForm.jsx
│       ├── FeedbackForm.module.css
│       └── README.md
├── README.md
├── INTEGRACIÓN.md
├── PARA_LOS_EQUIPOS.md
├── docker-compose.yml
└── .env.example
```

**Verificación:**
```bash
# Desde la raíz del proyecto:
find . -name "MVC_EXPLICADO.md" -o -name "models.py" -o -name "Login.jsx" | wc -l
# Debería mostrar 3 (una línea por cada archivo encontrado)
```

---

## 3. Setup Local: Backend

### Paso 1: Instalar Dependencias
```bash
cd backend
pip install -r requirements.txt
```

**Verificación:**
```bash
python -c "import sqlalchemy; import passlib; import jose; print('✅ Todas las librerías instaladas')"
```

Expected: `✅ Todas las librerías instaladas`

### Paso 2: Crear .env
```bash
cp .env.example .env

# Generar SECRET_KEY:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Copiar el output en .env
```

**Verificación:**
```bash
grep "SECRET_KEY" .env | grep -v "^#"
# Debería mostrar: SECRET_KEY=<tu_clave_aqui>
```

### Paso 3: PostgreSQL
```bash
cd ..
docker-compose up
```

**Verificación en los logs:**
- Buscar: `"database system is ready to accept connections"`
- Esperar ~10 segundos

---

## 4. Verificación Backend Inicial

```bash
cd backend

# ¿Pueden importar los módulos?
python -c "from models import Base; from database import Base as Base2; print('✅ Imports OK')"
```

Expected: `✅ Imports OK`

---

## 5. Setup Frontend

```bash
cd frontend
npm install
```

**Verificación:**
```bash
ls node_modules | wc -l
# Debería ser > 100 (dependencias instaladas)
```

---

## 6. Levanta Todo Junto

Abre 3 terminales:

**Terminal 1: PostgreSQL (ya corriendo desde Paso 3)**
```bash
# Ya debería estar corriendo, o:
docker-compose up
```

**Terminal 2: Backend**
```bash
cd backend
python -m uvicorn main:app --reload
```

Expected logs:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Terminal 3: Frontend**
```bash
cd frontend
npm start
```

Expected:
- Navegador abre en http://localhost:3000
- Ves una página (puede ser en blanco o con algo)
- No hay errores rojos en la consola del navegador

---

## 7. ¿Están Listos Los XXX TODO?

Busca en los archivos:

```bash
# Backend
grep -r "XXX TODO" backend/*.py | wc -l
# Debería mostrar ~27

# Frontend  
grep -r "XXX TODO" frontend/src/components/ | wc -l
# Debería mostrar 0 (no hay TODO en los componentes finales)
```

---

## 8. Documentación: ¿Puedo Leerla?

Abre estos archivos y verifica que tienen contenido:

- [ ] `docs/MVC_EXPLICADO.md` → Explica arquitectura
- [ ] `docs/JWT_SETUP.md` → Guía paso a paso
- [ ] `docs/FORMULARIOS_GUIA.md` → Enseña React formularios
- [ ] `INTEGRACIÓN.md` → Cómo integrar sin romper nada
- [ ] `docs/FRONTEND_PROFESIONAL.md` → Por qué UI/UX importa

---

## 9. ¿Qué Significan Los XXX TODO?

Busca uno y léelo:

```bash
grep -A2 "XXX TODO" backend/auth.py | head -5
```

Example output:
```
# XXX TODO: from passlib.context import CryptContext
```

**Verificación:** Cada XXX TODO tiene un comentario corto explicando qué implementar.

---

## 10. ¿Puedo Ver Los Componentes Reales?

```bash
cat frontend/src/components/Auth/Login/Login.jsx | head -20
```

Expected:
- Ves código React
- Tiene comentarios pedagógicos
- Dice `import { useState }`

```bash
cat frontend/src/components/Feedback/FeedbackForm/FeedbackForm.jsx | head -5
```

Expected:
- Ves otro componente similar (patrón reutilizado)

---

## 11. Resumen: ¿Estoy Listo?

Si pasaste estos checks, ¡**estás listo para empezar!**

- [ ] Todos los archivos existen en la estructura correcta
- [ ] Instalé dependencias (Python + Node)
- [ ] Docker + PostgreSQL funciona
- [ ] Backend levanta sin errores
- [ ] Frontend carga en http://localhost:3000
- [ ] Puedo ver ~27 XXX TODO en backend
- [ ] Puedo leer la documentación
- [ ] Los componentes React existen y tienen código

---

## 12. Si Algo Falla

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError` en backend | `pip install -r requirements.txt` |
| `docker-compose up` falla | `docker --version` (Docker debe estar corriendo) |
| `npm install` tarda mucho | Normal, espera 2-3 minutos |
| Frontend en blanco | Abre DevTools (F12), busca errores rojos |
| Backend dice "Error: port 8000 in use" | Mata el proceso: `lsof -ti :8000 \| xargs kill -9` |
| PostgreSQL connection refused | Espera a que `docker-compose up` muestre "database system is ready" |

---

## 13. Próximo Paso: Qué Leer Primero

Una vez verificado todo:

1. **Lee `docs/MVC_EXPLICADO.md`** (20 min) → Entiendes la arquitectura
2. **Abre `docs/JWT_SETUP.md`** → Guía de implementación paso a paso
3. **Si no hiciste React:** Lee `docs/FORMULARIOS_GUIA.md` (20 min)
4. **Empeza a implementar:** Busca `XXX TODO` en `backend/models.py`

---

> ✅ Del Unicornio: Verificación es tu amiga. Si todo pasa aquí, implementación será mucho más fácil.

