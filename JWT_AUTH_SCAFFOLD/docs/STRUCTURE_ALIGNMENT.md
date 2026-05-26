# 🔄 Alineación de Datos: CSV → Base de Datos

**Objetivo:** Mapear los datos del CSV original a las nuevas tablas SQL.

---

## Estructura Original (CSV)

Tu dataset principal tiene:
```
title, author, genres, rating, review_content, sentiments, recommendations
```

---

## Nuevas Tablas SQL

```
users
├── email
├── password_hash
└── created_at

user_reviews
├── id
├── user_email (FK)
├── book_title
├── review_text
├── rating
└── created_at
```

---

## Cómo Se Mezclan

1. Búsqueda original: CSV con datos históricos
2. Retroalimentación: Usuario agrega review a `user_reviews`
3. Análisis mejorado: Sentiment analyzer lee AMBAS fuentes

---

## Mapeo de Campos

| CSV | BD | Notas |
|-----|----|----|
| review_content | review_text | Mismo contenido |
| (búsqueda) | book_title | Título exacto |
| (usuario) | user_email | Email registrado |
| (rating) | rating | 1-5 |

---

> 🦄 Del Unicornio: Datos viejos + nuevos = mejores recomendaciones.
