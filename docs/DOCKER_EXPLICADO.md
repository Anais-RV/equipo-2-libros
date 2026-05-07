# 🐳 Docker Explicado — Lo que Necesitan Saber

*(Nota del unicornio que se piró: si no entienden Docker en la primera semana, es normal. Yo tampoco, por eso dejé esto documentado. Suerte.)*

---

## ¿Qué es Docker?

Docker es **una caja de seguridad virtual** donde vive todo lo que necesita el proyecto:
- Python 3.13 (sí, específicamente 3.13, no 3.12 ni 3.11)
- Node 18 (también específico, porque los detalles importan)
- BERT, Torch, todas las librerías pesadas (que pesan MUCHO)
- Configuración exacta (que tardé semanas en que funcionara)

**Ustedes editan el código en su máquina. Docker lo ejecuta dentro de la caja. Así su sistema está protegido.**

*Traducción: no carguen BERT en su máquina directamente o llorarán.*

---

## ¿Por qué Docker? (Una historia real)

### Lo que pasó sin Docker (el dolor)
```
Yo: "Listo, instalé BERT"
Mi compu: *comienza a arder*
RAM: 0.2GB disponible
Compu: ¿Quieres instalar más? Toma 2GB de swap.
Yo: "¿Por qué todo es tan lento?"
Compu: Porque instalaste 47GB de dependencias de ML.
Mi vida: destruida.
```

### Lo que pasa con Docker (salvación)
```
Ustedes: docker-compose up
Docker: "Yo manejo todo adentro de mi caja"
Su compu: Limpia. Feliz. Sin BERT contaminando el sistema.
Su vida: salvada.
```

---

## Las 4 razones por las que Docker existe (y yo lo uso)

### 1️⃣ Aislamiento (es decir, no contaminar tu compu)
**Sin Docker:** 
- Instalan BERT, torch, transformers → 47GB de dependencias
- Instalan Node → más cosas
- Python 3.13, esperen en realidad necesito 3.12 → conflictos
- Tu compu: "¿Quién soy? ¿Para qué sirvo?"

**Con Docker:**
- Toda la basura vive DENTRO del contenedor
- Tu compu: "Estoy limpia y feliz"
- Cuando cierras Docker: `docker-compose down` → adiós basura, código sigue en Git ✅

### 2️⃣ Consistencia (el "funciona en mi máquina" nunca más)
**Problema real que me pasó:**
```
Yo: "Funciona. Lo subo a GitHub"
Ustedes clonan: "No funciona"
Yo: "¿Qué? Para mí funciona..."
Ustedes: "Tienes Python 3.13, yo 3.12"
Yo: *cara de sufrimiento*
```

**Solución Docker:**
Todos tienen Python 3.13 exacto. Node 18 exacto. BERT exacto. Fin.
Si funciona en tu máquina = funciona en la de TODOS.

### 3️⃣ Reproducibilidad (para que en 2030 alguien sepa qué hacer)
En 6 meses, otro dev clona el repo y hace `docker-compose up`.
Funciona igual. Sin "ah, necesitas instalar X versión de Y en tu máquina antes de que el cometa golpee la tierra".

GitHub es tu fuente de verdad. Docker garantiza que funcione.

### 4️⃣ Profesional (así trabaja la industria real)
Startups, empresas, todo usa Docker. Si quieren trabajar en un equipo real después del bootcamp, esto ES lo que van a hacer.
Sin Docker = atraso de 5 años.

---

## Cómo lo usan (paso a paso)

### Primer día (Jueves 7 de mayo)

```bash
# 1. Clonan
git clone https://github.com/Anais-RV/equipo-2-libros.git
cd equipo-2-libros

# 2. Levantan Docker (ejecuta TODO el proyecto)
docker-compose up

# Esperen 2-3 minutos a que levante
# Verán:
# ✅ backend_1 | Uvicorn running on http://0.0.0.0:8000
# ✅ frontend_1 | webpack compiled...
# Sin errores rojos = TODO BIEN

# 3. Abren navegador
# http://localhost:3000  ← Frontend
# http://localhost:8000/docs  ← API docs (Swagger)

# 4. Trabajan normalmente
# - Editan código en VSCode (en su máquina)
# - Docker lo ejecuta en vivo
# - Los cambios se ven al instante
```

### Cada sesión (Lunes-Viernes)

```bash
# MAÑANA: Levantar Docker
docker-compose up
# (Espera 30 seg a que esté listo)

# TODO EL DÍA: Trabajan normalmente
# - Editan archivos
# - Git commit/push
# - Docker ejecuta en vivo

# TARDE: Cerrar Docker
Ctrl+C  (en la terminal de Docker)
docker-compose down
# (El contenedor se cierra, el código sigue en tu máquina y en Git)
```

---

## Qué entienden cuando hacen esto

### Editan código (su máquina local)
```python
# backend/analysis/sentiment_analyzer.py
def analyze_sentiment(text):
    # Ustedes escriben acá
    pass
```

### Docker lo ejecuta (dentro del contenedor)
```
Docker ejecuta el código ↓
Backend responde en http://localhost:8000
Frontend lo ve en http://localhost:3000
```

### Lo guardan
```bash
git add .
git commit -m "Implement sentiment analysis"
git push origin feature/sentiment
```

**El código VIVE en su máquina + Git. Docker es solo la ejecución.**

---

## Errores comunes (y soluciones)

### "Port 8000 already in use"
```bash
# Alguien más usa ese puerto
# Solución: Cierra Docker en otra terminal (Ctrl+C, docker-compose down)
# O usa puerto diferente (no lo hagan sin preguntar)
```

### "Cannot connect to Docker daemon"
```bash
# Docker Desktop no está corriendo
# Solución: Abre Docker Desktop (icono en aplicaciones)
# Espera 30 seg
```

### "Module not found"
```bash
# Docker no instaló las librerías
# Solución: Cierra Docker (Ctrl+C, docker-compose down)
# Abre de nuevo: docker-compose up --build
```

### "BERT is slow / consuming RAM"
```bash
# Normal. BERT es lento. Docker maneja la RAM.
# No es bug, es característica.
# Solución: Paciencia. Usen cache (ya implementado).
```

---

## Checklist cada mañana

- [ ] Docker Desktop abierto (ballena en tareas)
- [ ] `docker-compose up` corriendo
- [ ] Backend responde: `curl http://localhost:8000/health`
- [ ] Frontend carga: http://localhost:3000
- [ ] Cero errores rojos en la terminal

Si todo ✅ = a trabajar.

---

## Lo más importante

**Docker NO es mágico. Es una herramienta.**

- ✅ Usen `docker-compose up` cada mañana
- ✅ Trabajen normal (editen código, hagan commits)
- ✅ Cierren con `docker-compose down` cada tarde
- ✅ El código se guarda en Git (no desaparece)

**No teman a Docker. Es su aliado.**

---

## ¿Preguntas?

Discord → #equipo-2 (o #equipo-1)

Cualquier problema = pregunten. Para eso estamos.

---

**Analogía final:**

Docker es como un simulador de máquina real. Adentro, todo funciona exacto. Afuera, su compu está intacta. El código vive en su máquina. Docker es solo el "execute button".

Fin. 🚀
