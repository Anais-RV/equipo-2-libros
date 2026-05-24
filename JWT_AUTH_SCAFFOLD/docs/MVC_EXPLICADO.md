# 🦄 MVC: La Arquitectura que Van a Implementar

> Del unicornio que finalmente se quedó. Esto explica POR QUÉ estructuramos el código así.

---

## El Problema: "¿Dónde va cada cosa?"

Cuando crecen los proyectos, todo va en main.py y se convierte en un caos.

**Solución: MVC (Model-View-Controller)**

```
USER
  ↓
VIEW (Login.jsx)          ← Lo que ve el usuario
  ↓ POST /register
CONTROLLER (main.py)      ← La lógica de qué hacer
  ↓ sqlalchemy
MODEL (models.py)         ← Cómo guardar en BD
  ↓ SQL
DATABASE (PostgreSQL)     ← Donde viven los datos
```

---

## En Tu Proyecto

```
backend/
├── main.py              ← CONTROLLER (endpoints)
├── models.py            ← MODEL (tablas BD)
├── database.py          ← DATABASE (conexión)
├── auth.py              ← HELPERS (seguridad)
└── analysis/            ← (ya está, no cambia)

frontend/
└── components/
    └── Login.jsx        ← VIEW (formulario)
```

---

## Lee JWT_SETUP.md para empezar

> 🦄
