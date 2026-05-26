# 🚀 Deploy a Render (Producción)

**Objetivo:** Desplegar tu app online en 30 minutos.

---

## 0. Requisitos

- [ ] Backend funcionando localmente
- [ ] Frontend funcionando localmente
- [ ] Código commiteado en Git
- [ ] Cuenta en Render.com (gratis)

---

## 1. PostgreSQL en Render

1. Ve a https://render.com → Nuevo servicio → PostgreSQL
2. Nombre: `book-recommendations-db`
3. Copia el connection string
4. Crear servicio

---

## 2. Backend Deploy (FastAPI)

1. Nuevo servicio → Web Service
2. Conectar tu repo
3. Build: `pip install -r backend/requirements.txt`
4. Start: `uvicorn backend.main:app --host 0.0.0.0`
5. Variables de entorno:
   ```
   DATABASE_URL=<tu_connection_string>
   SECRET_KEY=<tu_secret_key>
   FRONTEND_URL=https://<tu-frontend>.onrender.com
   ```
6. Deploy

---

## 3. Frontend Deploy (React)

1. Nuevo servicio → Static Site
2. Conectar tu repo
3. Build command: `cd frontend && npm install && npm run build`
4. Publish directory: `frontend/build`
5. Deploy

---

## 4. Integrar URLs

En tu `frontend/.env`:
```
REACT_APP_API_URL=https://<tu-backend>.onrender.com
```

Cambiar los `fetch()` a:
```jsx
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

fetch(`${API_URL}/auth/login`, { ... })
```

---

## 5. Test

- Backend: https://<tu-backend>.onrender.com/docs
- Frontend: https://<tu-frontend>.onrender.com

---

> 🦄 Opcional: Si todo funciona, tu presentación final será online.
