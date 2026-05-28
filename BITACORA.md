# 📓 Bitácora del Proyecto · EMORA

> *"Un proyecto no se documenta para los demás: se documenta para tu yo de dentro de tres semanas."*

Este es el Evangelio del viaje de **· Juansucristo y sus apóstoles, según el equipo 2.**. Aquí recogemos, semana a semana, lo que hemos hecho, lo que nos ha costado, lo que hemos ido aprendiendo a base de horas, cafés, risas, llantos, cenas, discrepancias y las demás maravillas de trabajar en equipo, sabiendo cuándo poner la otra mejilla y seguir con los horarios previstos. No pretende ser una memoria final pulida: es un registro honesto del proceso, con sus dudas y resoluciones, en su mayoría autogestionadas y buscando ser siempre resolutivos y eficientes.

---

## 🧭 Visión general

**Objetivo:** construir un sistema de recomendación de libros basado en el **perfil emocional** de cada persona, recomendando libros en base a las emociones de los lectores, derivado de reseñas reales de la biblioteca en cuestión.

**Hipótesis:** dos libros con perfiles emocionales similares producen experiencias de lectura comparables, independientemente de su género nominal. 

**Restricción dura inicial:** procesar el dataset completo llevaba ~18 horas → el cacheo es parte de la arquitectura, no un *nice-to-have*. *(Spoiler de la semana 3: lo bajamos a 36 segundos.)*

**Restricción real:** procesar tal cantidad de libros y de emociones por parte de un humano, es algo prácticamente imposible, a esta aplicación le lleva unos minutos y con precisión.
---

## 📅 Línea temporal

| Semana | Foco | Archivo(s) clave | Estado |
| :---: | --- | --- | :---: |
| 1 | Exploración y limpieza de datos  | `data_processor.py` | ✅ Cerrada |
| 2 | Análisis de sentimientos · primera iteración.  | `sentiment_analyzer.py` · `cache_manager.py` | ✅ Cerrada |
| 3 | Optimización + recomendador + frontend + auth | `sentiment_analyzer.py` (v2) · `recommender.py` · `train_naive_bayes.py` · `auth.py` | ✅ Cerrada |
| 4 | Integración final, testing y demo | `main.py` + React |  ✅ Cerrada |
| 5 | Actualizaciones e implementación de mejoras | ✅ Cerrada |
---

## 📍 Semana 1 · Exploración y limpieza

**Fechas:** 7 — 11 mayo &nbsp;·&nbsp; **Foco:** entender el dataset y dejarlo limpio. &nbsp;·&nbsp; **Archivo clave:** `data_processor.py`

### 🎯 Objetivos
- Entender la estructura del dataset de Kaggle  (`Book_Details.csv` + `book_reviews.db`).
- Detectar valores nulos, duplicados, idiomas mezclados y campos ruidosos.
- Dejar una base limpia y reproducible para el resto del pipeline.
- Configuración en todos los equipos del Docker con el contenedor del proyecto.


### ✅ Lo que conseguimos
- Cargamos las ~63.000 reseñas y las cruzamos con los metadatos de libros.
- Identificamos los campos críticos para el modelo (texto de reseña, id de libro, rating).
- Diseñamos el primer pipeline de limpieza dentro de `data_processor.py`.
- Resolvimos parte del bloqueo de **Docker** (actualización de WSL) .

### 🧗 Retos
- Decidir qué hacer con reseñas muy cortas o en idiomas no ingleses.
- Equilibrar limpieza agresiva *vs.* perder señal emocional.
- Nuestro mayor reto: trabajar con Docker en vez de entorno virtual → conseguir que a todos nos funcionara sin que nos explotaran los equipos.
- Brainstorming inicial sobre el enfoque del modelo: empezamos pensando en **sentence-transformers para búsqueda semántica**, pero al releer el brief y debatirlo **en equipo** vimos que la aproximación correcta era **clasificación de emociones**. Y de ahí, otra capa: no nos bastaba con un zero-shot genérico — queríamos que el modelo realmente *entendiera* las emociones, así que la idea evolucionó hacia **transfer learning** (modelo pre-entrenado para emociones) + **un clasificador propio entrenado por nosotros** como segundo flujo. 

### 💡 Aprendizajes
- **Docker reemplaza al venv**, pero hay que recordar reconstruir (`docker compose up --build`) cada vez que tocamos `requirements.txt`. Muy divertido.
- **La calidad del dataset es el techo del modelo.** Cada decisión aquí condiciona todo lo demás.
- Leer el brief con atención antes de elegir herramientas quizás nos ahorra muchas horas.

### 🔜 Próximos pasos
- Pasar el dataset limpio a la fase de clasificación emocional.

---

## 📍 Semana 2 · Análisis de sentimientos · primera iteracción

**Fechas:** 12 — 18 mayo &nbsp;·&nbsp; **Foco:** convertir cada reseña en un vector de probabilidades emocionales. &nbsp;·&nbsp; **Archivo clave:** `sentiment_analyzer.py`

> 🔥 La semana más densa en decisiones de modelo: aquí elegimos el corazón del proyecto.

### 🎯 Objetivos
- Implementar `sentiment_analyzer.py` con un pipeline de 🤗 `transformers`.
- Clasificar cada reseña en 6 emociones: **alegría, tristeza, miedo, enfado, sorpresa, asco** (las 6 básicas de Ekman).
- Validar que `cache_manager.py` guarda los resultados correctamente (sin esto, cada cambio = 18 h de recálculo).
- Generar el **perfil emocional por libro** promediando las emociones de sus reseñas.
- Que nos funcione el Docker a todos.

### ✅ Lo que conseguimos
- Primera versión de `sentiment_analyzer.py` funcionando con **`j-hartmann/emotion-english-distilroberta-base`** — un DistilRoBERTa fine-tuneado específicamente para las 6 emociones de Ekman.
- `cache_manager.py` implementado y funcionando: nunca volvemos a recalcular lo ya hecho.
- Primer recommender básico con cosine similarity sobre los perfiles emocionales.
- Documentación interna en `docs/`: arquitectura, brief para nosotros mismos, "notas del unicornio" 🦄.

### 🧗 Retos
- **Tiempos de procesamiento prohibitivos** con la configuración por defecto del pipeline (fp32, sin batching real, `max_length=512`). El cálculo entero se iba a horas.
- Distinguir **BERT (búsqueda semántica)** de **DistilRoBERTa fine-tuneado para clasificación**: no es lo mismo, y lo aprendimos a base de leernos los papers y los model cards.
- Decidir cómo manejar libros con muy pocas reseñas: dejamos `MAX_REVIEWS=35` como techo, sabiendo que más adelante veríamos si era realista.

### 💡 Aprendizajes
- **DistilRoBERTa fine-tuneado >> zero-shot genérico** para nuestro caso. El modelo de j-hartmann ya viene entrenado sobre las emociones exactas que queríamos, así que los scores son más estables y discriminativos. Y de paso es ~3× más pequeño y rápido.
- Añadir una librería al proyecto = editar `requirements.txt` + `docker compose up --build`. Sin atajos.
- Entender qué es y cómo funciona BERT (y por qué DistilRoBERTa es más adecuado aquí).
- El transfer learning es potente, pero **no es gratis**: cada inferencia cuesta, y el caché es nuestro mejor amigo.

### 🔜 Próximos pasos
- Optimizar el sentiment analyzer en serio: o bajamos los tiempos a minutos o el proyecto no llega a tener demo.
- Pulir el recommender y exponerlo bien desde la API.
- Empezar el frontend en condiciones.
- Que nos funcione el Docker, este objetivo ya es parte de nosotros.


---

## 📍 Semana 3 · Optimización + recomendador + frontend + auth

**Fechas:** 19 — 25 mayo &nbsp;·&nbsp; **Foco:** pasar de prototipo lento a producto completo. &nbsp;·&nbsp; **Archivos clave:** `sentiment_analyzer.py` (TURBO v2), `recommender.py`, `train_naive_bayes.py`, `auth.py`

> 🚀 La semana del "esto sí va a funcionar". Cuatro frentes abiertos en paralelo y cuatro frentes cerrados al final.

### 🎯 Objetivos
- Optimizar el sentiment analyzer para que el procesamiento entero baje de horas a minutos.
- Refactorizar el recommender y exponerlo correctamente desde FastAPI.
- Frontend nuevo con visualizaciones del perfil emocional.
- Autenticación de usuarios con JWT para poder recoger feedback.
- Añadir un **segundo flujo** entrenado por nosotros que valide los perfiles emocionales.

### ✅ Lo que conseguimos

**🧠 Sentiment Analyzer · TURBO v2** *(PRs #22, #24, #27)*
- **`fp16`** → modelo en media precisión, ≈2× speedup sin pérdida apreciable.
- **Length bucketing** → ordena textos por longitud antes de batchear (2-3× speedup, fuera padding desperdiciado).
- **`max_length=128`** → 4× menos cómputo que el default de 512.
- **Pre-indexado de reviews por `book_id`** con `groupby` → eliminamos el bucle O(n²) que arrastrábamos.
- **Batch size 512** + **checkpoints incrementales** cada 500 libros.
- **Resultado final: ~36 segundos** para procesar el dataset entero en una RTX 5060 Ti. De "18+ horas" a "tiempo para tomarse un café". *Esto no es una errata.*

**🎯 Recommender refactorizado** *(PR #24)*
- `recomendar_por_afinidad_emocional()` y `find_similar_books()` separados, limpios y testeables.
- Recomendaciones **precomputadas** en `all_book_recommendations.csv` → la API responde en milisegundos.
- Endpoints expuestos: `/recommend`, `/recommendations/emotional`, `/recommendations/precomputed`, `/profiles/search/by-title`, etc.

**🎲 Naive Bayes propio como segundo flujo** *(PR #27)*
- `train_naive_bayes.py`: entrenamos un GaussianNB sobre `emotion_profiles.csv` usando la emoción dominante (`idxmax`) como etiqueta. **Esta es la "IA entrenada por nosotros"** que decidimos en la semana 1.
- Sirve como **validador** del flujo de DistilRoBERTa: si Naive Bayes predice bien la emoción dominante, los perfiles son consistentes.
- Documentado en `docs/BAYES_VALIDADOR.md`.

**🎨 Frontend nuevo** *(PR #25)*
- Componentes: `EmotionRadar`, `EmotionBars`, `BookCard`, `MetricPill`, `LoadingSpinner`, `RecommendationForm`, `ResultsDisplay`, `Auth`.
- Visualización del perfil emocional como radar chart → la recomendación es **explicable**, no una caja negra.
- Estructura `src/app`, `src/services`, `src/helpers` mucho más limpia que la versión inicial.

**🔐 Autenticación JWT** *(PRs #30 y #31)*
- `auth.py` con bcrypt + `python-jose` (tokens de 24h).
- `database.py` con SQLAlchemy + `models.py` (`User`, `UserReview`) + `schemas.py` (Pydantic).
- Endpoints: `/auth/register`, `/auth/login`, `/user/me`, `/user/feedback`.
- El feedback se guarda en BBDD → base para reentrenamiento supervisado en futuras iteraciones.

### 🧗 Retos
- **De los 16.225 libros del dataset, solo 13.149 tienen reviews disponibles** en `reviews_clean.csv`. Los ~2.851 restantes simplemente no aparecen → media de **~4 reviews/libro**, así que el `MAX_REVIEWS=35` casi nunca se alcanza en la práctica. Bueno saberlo para gestionar expectativas en la demo (y entender por qué algunos libros se quedaron fuera, no es un bug).
- **Conflictos de merge en la rama JWT** que nos costaron una tarde. Lección: rebasear antes y más a menudo cuando varias ramas tocan `requirements.txt` y `main.py`.
- **Imports relativos rotos en `analysis.recommender`** al reorganizar la estructura. Resuelto.
- `requirements.txt` duplicado en raíz y en `backend/` causaba confusión sobre qué se instalaba en Docker → unificado en `backend/requirements.txt` y borrado el de la raíz.
- Seguimos insistiendo con Docker, pero no quiere colaborar, así que se baraja seguir con ello o sustituirlo por venv.

### 💡 Aprendizajes
- **Las optimizaciones de inferencia se multiplican, no se suman.** Ninguna de las 4 técnicas por separado habría sido suficiente; juntas, mágicas.
- **Recomendaciones precomputadas + caché** = latencia trivial sin tener que tocar la inferencia en producción.
- **Conocer los límites reales del dataset evita debuggear bugs que no existen.** Cuando un libro no devuelve perfil, ahora sabemos que no es el código: es que no había reviews.
- Las ramas largas son nuestro enemigo. Las PRs pequeñas y frecuentes, nuestra amiga.

### 🔜 Próximos pasos
- Integración end-to-end: probar el flujo completo *register → login → recomendación → feedback* con el frontend real.
- Escribir tests con `pytest` (ya está en `requirements.txt`, falta hacer el trabajo).
- Preparar la demo: scripts de carga, instrucciones claras, fallbacks bonitos cuando el modelo no encuentra el libro.
- Pasamos de Docker, por problemas técnicos, decidimos sustituirlo por nuestro ya conocido entorno virtual, que seguro que no nos va a fallar.

---

## 📍 "Semana 4" · Integración final, testing y demo 

**Fechas:** 25 mayo — 27* &nbsp;·&nbsp; **Foco:** que esto se pueda **usar**, no solo demostrar.

### 🎯 Objetivos previstos
- Cerrar la integración React ↔ FastAPI con el flujo de auth incluido.
- Tests con `pytest` para los endpoints críticos.
- Diseñar la demo: el usuario introduce un libro o estado emocional → recibe recomendaciones explicadas con radar chart.
- Documentación final: README pulido, instrucciones de despliegue claras.
- Preparar diapositivas y presentación de proyecto + visión de negocio.
- Todos con el entorno virtual funcionando.
- Ya que estamos enganchados al proyecto, ya tenemos pensadas nuevas implementaciones para seguir trabajando con ello.

### 🤔 A discutir en equipo
- ¿Filtramos por género, autor o idioma antes de calcular la similitud, o dejamos que el usuario lo controle desde el frontend?
- ¿Qué libros usamos como "ejemplos estrella" en la presentación?
- ¿Cómo enseñamos el flujo de Naive Bayes en la demo sin perder al público?


---

## 🛠️ Decisiones técnicas relevantes

| Decisión | Por qué |
| --- | --- |
| **DistilRoBERTa fine-tuneado (`j-hartmann/emotion-english-distilroberta-base`)** | Modelo entrenado específicamente sobre las 6 emociones de Ekman → scores más estables y discriminativos que un zero-shot genérico. Y de paso es ligero y rápido. |
| **Naive Bayes propio como segundo flujo** | Validador independiente entrenado por nosotros sobre los perfiles emocionales. Si NB predice bien la emoción dominante, los perfiles son consistentes. |
| **Cuádruple optimización (fp16 + length bucketing + max_length=128 + pre-indexado)** | De ~18 h a ~36 segundos. Ninguna de las 4 técnicas por separado era suficiente. |
| **Recomendaciones precomputadas en CSV** | Calculamos una vez, servimos millones de veces. Latencia trivial. |
| **Docker Compose** | Reproducibilidad para todo el equipo + separación clara backend/frontend. |
| **Caché obligatorio (`cache_manager.py`)** | Decisión arquitectónica del día 1, no parche posterior. |
| **Similitud coseno** | Estándar interpretable y eficiente para vectores de baja dimensión (6 emociones). |
| **6 emociones básicas (Ekman)** | Cubre el espectro afectivo principal sin diluir la señal en categorías difusas. |
| **JWT en lugar de sesiones** | Stateless, encaja con FastAPI, escala sin Redis. |

---

## 📚 Recursos y referencias

- 🤗 [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) · el modelo de emociones
- 📦 [Goodreads Book Reviews · Kaggle](https://www.kaggle.com/) · el dataset
- 📖 [FastAPI · documentación oficial](https://fastapi.tiangolo.com/)
- 🐳 [Docker Compose · docs](https://docs.docker.com/compose/)
- 🔐 [JWT con FastAPI · tutorial oficial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- 📊 [scikit-learn · Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html)

---

## 📝 Convenciones de la bitácora

Para que esto siga siendo útil dentro de tres semanas:

- Cada entrada semanal tiene **5 secciones fijas**: Objetivos · Lo conseguido · Retos · Aprendizajes · Próximos pasos.
- Si una decisión se revierte, **no se borra**: se tacha y se anota por qué. La trazabilidad importa más que la limpieza.
- Cualquiera del equipo puede añadir una entrada extraordinaria si lo cree conveniente (un debate, un descubrimiento, un *post-mortem*).
- Las preguntas abiertas se quedan en la bitácora hasta que se resuelven explícitamente.

---

<p align="center">
  <sub>📓 Última actualización: <i>25 mayo 2026</i> &nbsp;·&nbsp; mantenida con cariño por el <b>Equipo 2 · Libros</b></sub>
</p>
