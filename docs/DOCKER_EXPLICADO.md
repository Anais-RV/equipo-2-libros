# 🐳 Docker Explicado — Lo que Necesitan Saber

*(Nota del unicornio que se piró: si no entienden Docker en la primera semana, es normal. Yo tampoco, por eso dejé esto documentado. Suerte.)*

---

## 🚀 PRIMER PASO: Instalar Docker Desktop

**Si no lo tienen aún, comiencen por acá. No pueden hacer nada sin esto.**

### Windows (Lo más probable)

1. **Descargen Docker Desktop:** https://www.docker.com/products/docker-desktop
2. **Ejecuten el instalador** (.exe que bajaron)
3. **Acepten TODOS los permisos** que pide (importante)
4. **Reinicien la máquina** (sí, obligatorio. No lo salten.)
5. **Abran Docker Desktop** (icono en aplicaciones o bandeja de tareas)
   - Busquen la ballena azul 🐳
   - Esperen a que diga "Docker Desktop is running"
   - Puede tardar 1-2 minutos la primera vez

**Verificar que funciona:**
```bash
# Abran PowerShell y corran:
docker --version
# Deberían ver algo como: Docker version 24.0.0, build xxxxx
```

Si ven un error "Cannot connect to Docker daemon":
- Abran Docker Desktop (icono en taskbar, esquina inferior derecha)
- Esperen 30 segundos
- Reintenten el comando

### macOS

1. **Descargen Docker Desktop:** https://www.docker.com/products/docker-desktop (versión Mac Intel o Apple Silicon según su chip)
2. **Ejecuten el .dmg** y arrastren Docker a Applications
3. **Abran Docker** desde Applications
4. **Acepten el password** si pide (es necesario para VM)

```bash
# Verificar en terminal:
docker --version
```

### Linux (Si alguien usa)

```bash
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Iniciar servicio:
sudo systemctl start docker
sudo systemctl enable docker
```

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
# O usa puerto 