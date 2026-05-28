# 📚 Sistema de Recomendación de Libros por Afinidad Emocional

Sistema de recomendación de libros basado en análisis de sentimientos emocionales extraídos de reseñas reales de Goodreads, con autenticación JWT y frontend React.

**Hipótesis de partida:** dos libros pueden ser muy diferentes en género, autor o trama, pero producir en el lector el mismo tipo de impacto emocional. Ese eje emocional es el que muchos sistemas comerciales ignoran y que a nosotros nos ha parecido muy importante implementar en nuestro modelo.

---

## 🧠 Stack técnico

### Backend
- **Python 3.12** + **FastAPI** + **Uvicorn**
- **NLP:** `j-hartmann/emotion-english-distilroberta-base` (clasificación supervisada de 6 emociones básicas de Ekman)
- **Flujo alternativo:** Naive Bayes (validador independiente — ver `train_naive_bayes.py`)
- **ML:** scikit-learn (cosine similarity, vectorización)
- **Aceleración:** PyTorch con CUDA (fp16 + length bucketing → 16k libros procesados en ~36 segundos en RTX 5060 Ti)
- **Auth:** JWT + bcrypt (`backend/auth.py`)
- **Persistencia:** SQLite (`backend/libros.db`)
- **Traducciones de sinopsis:** Helsinki-NLP / `opus-mt-en-es`

### Frontend
- **React 18** + **Axios** + **lucide-react**
- Estructura modular: `components/`, `services/`, `helpers/`, `styles/`

### Infraestructura

- **Entorno virtual** .venv
- Hot-reload en ambos servicios para desarrollo
- **.env** clave secreta para JWT
---

## 📊 Dataset

| Métrica | Valor |
|---|---|
| Libros en catálogo | 16,225 |
| Libros con reviews disponibles | 13,149 |
| Reseñas totales | ~63,000 |
| Reviews por libro (media) | ~4 |
| Fuente | Kaggle · Goodreads Books Dataset |

> ℹ️ De los 16,225 libros del catálogo, solo 13,149 aparecen también en `reviews_clean.csv`. Los ~2,851 restantes se mantienen en el catálogo pero no obtienen perfil emocional propio.

---

## 🎨 Las 6 emociones del modelo

El clasificador devuelve, para cada review, la probabilidad de cada una de estas emociones (modelo de Ekman):

`joy` · `sadness` · `fear` · `surprise` · `anger` · `disgust`

El perfil emocional de un libro es el **promedio** de las predicciones sobre todas sus reviews (hasta 35 por libro, truncadas a 128 tokens).

---

## 🧰 Requisitos previos

| Herramienta | Versión |
|---|---|
| Python | 3.12.10 |
| Node.js | v24.16.0 |
| npm | 11.13.0 |

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd equipo-2-libros
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

**Windows:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias Python

```bash
pip install -r backend/requirements.txt
```

> ⚠️ **Sin GPU Nvidia:** Comenta las 4 líneas de `torch` en `backend/requirements.txt` e instala torch normal:
> ```bash
> pip install torch
> ```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo a la raíz del proyecto y rellena los valores:

```bash
cp backend/.env.example .env
```

Genera una clave secreta para JWT con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Y pégala como valor de `SECRET_KEY` en tu `.env`.

---

## 🔄 Pipeline de datos (ejecutar en orden)

Desde la raíz del proyecto con el entorno virtual activado:

### Paso 1 — Procesar datos
Genera el CSV limpio a partir del dataset original.
```bash
python backend/analysis/data_processor.py
python backend/analysis/translate_descriptions.py

```

### Paso 2 — Análisis de sentimientos
Entrena el modelo Naive Bayes y procesa el análisis de sentimientos con DistilRoBERTa.
```bash
python backend/analysis/train_naive_bayes.py
python backend/analysis/sentiment_analyzer.py
```

### Paso 3 — Sistema de recomendación
Genera el CSV de recomendaciones precalculadas.
```bash
python backend/analysis/recommender.py
```

---

## 🚀 Arrancar la aplicación

### Opción A — Local (recomendado para desarrollo)

Necesitas **dos terminales abiertas** al mismo tiempo:

**Terminal 1 — Backend (API)**
```bash
python backend/main.py
```
- API disponible en: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs

**Terminal 2 — Frontend (Web)**
```bash
cd frontend
npm install   # solo la primera vez
npm start
```
- Aplicación web en: http://localhost:3000

### Opción B — Docker

```bash
docker compose up --build
```

Para añadir dependencias Python: editar `backend/requirements.txt` y relanzar con `--build`.

---

## 🎯 Sistema de scoring

La afinidad entre dos libros se calcula con esta combinación lineal:

| Componente | Peso |
|---|---|
| Similitud emocional (cosine sobre las 6 emociones) | **70%** |
| Coincidencia de géneros | **20%** |
| Cercanía de rating | **7%** |
| Penalización por mismo autor | **3%** |

> La penalización por mismo autor evita que el sistema se vuelva un "más libros del mismo autor" y empuja al descubrimiento.

---

## 🌐 API · Endpoints disponibles

### Catálogo
- `GET /books` — listar libros con paginación
- `GET /books/{book_id}` — ficha completa de un libro
- `GET /search?title=...` — búsqueda por título

### Perfiles emocionales
- `GET /profiles` — lista de perfiles emocionales
- `GET /profiles/{book_id}` — perfil de un libro concreto
- `GET /profiles/search/by-title?title=...` — buscar perfil por título

### Recomendaciones
- `GET /recommendations/emotional?title=...` — recomendaciones por afinidad emocional
- `GET /recommend?title=...` — recomendación de compatibilidad general
- `GET /recommendations/precomputed?title=...` — recomendaciones precalculadas (modo rápido)

### Autenticación
- `POST /auth/register` — registro de usuario
- `POST /auth/login` — login (devuelve JWT)
- `GET /user/me` — perfil del usuario autenticado
- `POST /user/feedback` — registrar feedback sobre una recomendación

### Mantenimiento
- `GET /health` — health check
- `POST /reload` — recargar CSVs en memoria sin reiniciar

---

## 🗃️ Base de datos

El proyecto usa SQLite (`backend/libros.db`) con dos tablas:

- `users` — usuarios registrados (email + password hasheada con bcrypt)
- `user_reviews` — reseñas de libros por usuario autenticado

La base de datos se crea automáticamente al arrancar el backend por primera vez.

---

## 🗂️ Estructura del proyecto

```
equipo-2-libros/
├── backend/
│   ├── analysis/
│   │   ├── data_processor.py      # Paso 1: limpieza de datos
│   │   ├── train_naive_bayes.py   # Paso 2a: entrena modelo Bayes
│   │   ├── sentiment_analyzer.py  # Paso 2b: DistilRoBERTa + Naive Bayes
│   │   ├── recommender.py         # Paso 3: motor de recomendación
│   │   └── cache_manager.py       # Caché de perfiles emocionales
│   ├── auth.py                    # JWT + bcrypt
│   ├── database.py                # Conexión SQLite
│   ├── main.py                    # API FastAPI
│   ├── models.py                  # Tablas SQLAlchemy
│   ├── schemas.py                 # Validación Pydantic
│   ├── requirements.txt
│   └── .env.example               # Plantilla de variables de entorno
│
├── frontend/                      # Aplicación React
│   ├── src/
│   │   ├── components/
│   │   ├── services/              # Cliente axios
│   │   ├── helpers/
│   │   └── styles/
│   └── package.json
│
├── data/                          # CSVs (no versionados)
├── docs/                          # Documentación técnica
│   ├── ARQUITECTURA.md
│   ├── BAYES_VALIDADOR.md
│   ├── DOCKER_EXPLICADO.md
│   └── BRIEF_PARA_ESTUDIANTES.md
│
├── docker-compose.yml
├── .env                           # No versionado — copiar de backend/.env.example
└── README.md
```

---

## ⚡ Rendimiento

Procesamiento del dataset completo (16,225 libros) con `sentiment_analyzer.py`:

| Configuración | Tiempo |
|---|---|
| GPU (RTX 5060 Ti, fp16, batch=512, length bucketing) | **~36 segundos** |
| CPU (no recomendado) | Horas |

Optimizaciones aplicadas:
- Modelo en **fp16** (mitad de memoria, ~2× velocidad, sin pérdida apreciable)
- **Length bucketing** — agrupa textos por longitud antes de batchear
- **Pre-indexado de reviews por `book_id`** — elimina bucle O(n²)
- **`max_length=128`** — evita gasto de cómputo en padding innecesario
- **Checkpoints incrementales** cada 500 libros

---

## 👥 Equipo

| Rol | Nombre |
|---|---|
| _(por completar)_ | _(por completar)_ |

> _Sustituir esta tabla por la información definitiva del equipo._

---

## 📚 Documentación adicional

- [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) — Diagrama de flujo de datos y decisiones técnicas
- [`docs/BAYES_VALIDADOR.md`](docs/BAYES_VALIDADOR.md) — Cómo se usa Naive Bayes como segundo flujo de validación
- [`docs/DOCKER_EXPLICADO.md`](docs/DOCKER_EXPLICADO.md) — Setup y troubleshooting de Docker
- [`docs/BRIEF_PARA_ESTUDIANTES.md`](docs/BRIEF_PARA_ESTUDIANTES.md) — Onboarding para nuevos colaboradores
- [`BITACORA.md`](BITACORA.md) — Journal semanal del proyecto

---

## 📝 Notas

- Los CSVs grandes (`books_clean.csv`, `reviews_clean.csv`, `emotion_profiles.csv`) no se versionan — solicitar al equipo si se clona el repo desde cero.
- El modelo `j-hartmann/emotion-english-distilroberta-base` se descarga automáticamente la primera vez que se ejecuta `sentiment_analyzer.py`.
- El feedback que envían los usuarios autenticados se guarda en BBDD y se podrá usar en futuras iteraciones para reentrenamiento supervisado.
- El archivo `.env` (con la `SECRET_KEY` real) **nunca debe subirse al repositorio**. Solo se sube `.env.example` como plantilla.

---

_Proyecto Final · Bootcamp Data Analyst · Factoría F5_
