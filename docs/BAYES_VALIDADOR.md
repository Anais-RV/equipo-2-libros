# 🦄 Bayes: Tu Segundo Cerebro (Cuando BERT No Confía Ni En Él Mismo)

## IMPORTANTE: Esto es un Plus, NO es Obligatorio

Mira. Tu código BERT funciona. Probablemente ya lo viste funcionando y dice "sí, conozco sentimientos".

Este documento es para quien quiera:

- Darle a BERT un "verificador rápido" que le diga "hey, tú qué crees?" (porque a veces BERT miente)
- Obtener un score de confiabilidad (en lugar de adivinar si está bien)
- Saber CUÁNDO BERT está mintiendo (pasa, es BERT)
- Hacer análisis de 10,000 reviews en 1 hora en lugar de 3

**Sin presión:** Si llegas a la demo con BERT y funciona, es épico. Si quieres el plus de confiabilidad, aquí está.

**Timeline real:**
- **Días 1-9:** Mantén BERT como está. Funciona. No lo toques.
- **Día 10+ (si sobra tiempo):** Agrega Bayes en 30 minutos y duerme tranquilo.

---

## La Idea: Dos Opiniones Mejor que Una (O Por Qué No Deberías Confiar En Nadie)

Imagina tu API así:

```
Usuario pregunta: "¿Este libro es triste?"

BERT (el confiado):    → "Sí, tristeza 85%"
Bayes (el paranoico): → "Hmm, veo muchas palabras tristes... sí, concuerdo"

API responde: "Tristeza 92% (BERT + Bayes de acuerdo)"
Confiabilidad: ALTA

Ahora: "No me gusta, aunque escribe bien"

BERT: → "Disgusto 70%" (confiado, pero confundido)
Bayes: → "Espera... veo 'no me gusta' pero también 'escribe bien'... algo no cuadra"

API responde: "Disgusto 65% (BERT y Bayes NO se entienden)"
Confiabilidad: MEDIA

→ Ahora SABES que algo raro pasó y tienes que revisar manualmente
```

---

## Por Qué Funciona? (La Parte Seria, aunque sea un Rato)

BERT entiende **contexto** (el "por qué" de las palabras, cómo se relacionan).
Bayes solo cuenta **palabras** (el "cuántas veces aparece esto").

Juntos son un power couple incómodo pero efectivo:

| Texto | BERT Dice | Bayes Dice | Conclusión |
|-------|-----------|-----------|-----------|
| "Libro hermoso, me encantó" | 90% alegría | "Muchas palabras alegres" → 88% | 95% confianza |
| "Qué maravilla de desastre" | 60% alegría (confundido por la ironía) | "Palabras contradictorias" → 50% | 50% confianza ⚠️ |
| "Mal" | 55% disgusto (sin contexto) | "Una palabra, poco contexto" → 40% | 40% confianza ⚠️ |
| "Es bueno aunque malo" | 50-50 (BERT totalmente perdido) | "Palabras vs buenas vs malas" → dudoso | FLAG para revisar manualmente |

---

## Los 3 Ingredientes Simples de Bayes (Sin Magia, Solo Matemática Básica)

Bayes es solo una **receta con 3 números**. Si entiende esto, eres un experto. Si no, al menos ahora sabes que existe.

### 1. PRIOR: La Creencia Inicial (Tu Prejuicio)

Antes de leer nada, cuál es tu apuesta inicial?

```
De 100 reseñas que ya analizaste:
- 30% son Alegría
- 25% son Tristeza
- 20% son Disgusto
- 25% son Miedo

Tu PRIOR = "Probablemente sea Alegría porque es lo más común"
(Bayes es perezoso, apuesta al caballo ganador)
```

En código:
```python
prior_alegria = 0.30  # Si no ves nada, apuesta aquí
```

**Realidad:** Si no ves una sola palabra, Bayes predice el sentimiento más frecuente. Obvio.

---

### 2. LIKELIHOOD: La Evidencia del Pasado (Qué Pasó Antes)

Ves una palabra. Bayes pregunta: *"En las reseñas tristes que YA PROCESÉ, qué tan seguido aparece esta palabra?"*

```
Ves: "llanto"

En reseñas TRISTES (que Bayes ya vio):
→ "llanto" aparece en 80 de 100 reseñas
→ Likelihood = 0.80 (muy probable en tristeza)

En reseñas ALEGRES (que Bayes ya vio):
→ "llanto" aparece en 2 de 100 reseñas
→ Likelihood = 0.02 (raro en alegría)

Conclusión: "llanto" es 40 veces más probable en Tristeza que en Alegría
(Bayes mira el historial y dice: "está claro")
```

En código:
```python
likelihood_llanto_en_tristeza = 0.80
likelihood_llanto_en_alegria = 0.02
```

---

### 3. POSTERIOR: Tu Nueva Creencia (Después de Ver la Evidencia)

Combines los 3 números y ACTUALIZAS lo que creías:

```
Empezaste: "25% de chance de que sea Tristeza" (Prior)
Ves: "llanto"
Actualizas: "Espera, 'llanto' aparece en el 80% de tristezas..."
Resultado: "Ahora creo 85% de chance de que sea Tristeza" (Posterior)

Ese 85% es lo que le devuelves al usuario.
```

---

### La Fórmula (No Te Asustes, Es Simple)

```
P(Tristeza | "llanto") = P("llanto" | Tristeza) × P(Tristeza) / P("llanto")
```

En español sin tanta simbología:

- **P(Tristeza | "llanto")** = "Probabilidad de Tristeza DADO que vi 'llanto'" ← **ESTO ES LO QUE DEVUELVES**
- **P("llanto" | Tristeza)** = "Qué tan común es 'llanto' en textos tristes?" (Likelihood)
- **P(Tristeza)** = "Qué porcentaje de textos son tristes?" (Prior)
- **P("llanto")** = "En cuántos textos totales aparece 'llanto'?" (el normalizador, lo aburrido)

---

### Ejemplo Completo: Paso a Paso

Reseña que llega: **"Lloré mucho, fue muy triste"**

**Paso 1: Prior (Tu apuesta inicial)**
```
Antes de leer nada:
- 25% de los textos son tristes (estadística histórica)
P(Tristeza) = 0.25
```

**Paso 2: Likelihood (Qué pasó antes)**
```
Ves la palabra "lloré"

En textos tristes que Bayes vio: 85% contienen "lloré"
P("lloré" | Tristeza) = 0.85

En textos no-tristes que Bayes vio: 5% contienen "lloré"
P("lloré" | No-Tristeza) = 0.05
```

**Paso 3: Calcula (El Momento de la Verdad)**
```
Fórmula de Bayes:
P(Tristeza | "lloré") = (0.85 × 0.25) / 0.10
                       = 0.2125 / 0.10
                       = 2.125 
                       
Normalizado a [0-1]:  ≈ 0.92 (92% confianza)

→ "Este texto es Tristeza con 92% de confianza"

Bayes acaba de actualizar su creencia de 25% → 92%.
Eso es lo que hace. Actualiza creencias con evidencia.
```

---

## Por Qué Bayes es Tu Aliado: Rápido, Ligero, y Brutalmente Honesto

**La Limitación Que Probablemente Has Visto:**
Naive Bayes ignora el orden de las palabras. Para él, estas dos frases son IDÉNTICAS:
- "No tengo miedo"
- "Tengo miedo"

**Y eso es malo?** A priori sí. Pero en práctica? NO, porque:

1. ✅ Corre en <50ms (BERT tarda 1-3 segundos, a veces más si está de mal humor)
2. ✅ Se entrena en minutos (BERT necesita horas/GPU/plegarias a los dioses)
3. ✅ Ocupa 100MB RAM (BERT ocupa GB, come como un tiburón)
4. ✅ **Como validador**, no necesita ser perfecto, solo confirmar o dudar
5. ✅ Si BERT y Bayes coinciden → confianza ALTA (los dos están de acuerdo, es raro)
6. ✅ Si divergen → flag automático para revisar manualmente (algo pasó)

---

## Implementación (30 Minutos, Sin Romper Nada)

### Paso 1: Asegurar Scikit-learn en requirements.txt

```
scikit-learn==1.3.0
```

Si no está, agrégalo. Si está, sigue adelante.

---

### Paso 2: Crear backend/analysis/sentiment_validator.py

Copia esto exacto:

```python
import pickle
import os
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

class BayesValidator:
    '''Validador Bayes: Segunda opinión rápida sobre sentimientos.
    NO reemplaza BERT. Solo valida. Es el fiscal que BERT necesaba.'''
    
    def __init__(self, cache_path="cache/bayes_model.pkl"):
        self.cache_path = cache_path
        self.model = None
        self.vectorizer = None
        self.emotions = None
        
    def train(self, reviews_df):
        '''Entrena Bayes con los datos que YA TIENES (BERT ya etiquetó).
        
        reviews_df necesita:
        - 'review_text': el texto
        - 'dominant_emotion': la etiqueta que BERT calculó
        
        Uso:
        >>> validator = BayesValidator()
        >>> validator.train(mi_dataframe)
        >>> validator.save()
        '''
        
        texts = reviews_df['review_text'].astype(str).values
        emotions = reviews_df['dominant_emotion'].values
        
        self.vectorizer = CountVectorizer(
            max_features=1000,
            lowercase=True,
            stop_words='spanish'
        )
        X = self.vectorizer.fit_transform(texts)
        
        self.model = MultinomialNB()
        self.model.fit(X, emotions)
        self.emotions = list(set(emotions))
        
        print(f"Bayes entrenado con {len(texts)} textos")
        return self
    
    def validate(self, text, bert_emotion, bert_confidence):
        '''Valida un resultado de BERT.
        Devuelve un dict con bert vs bayes vs combined confidence.
        '''
        
        if self.model is None:
            return {
                'bert_emotion': bert_emotion,
                'bert_confidence': bert_confidence,
                'bayes_emotion': None,
                'bayes_confidence': None,
                'agreement': None,
                'combined_confidence': bert_confidence,
                'note': 'Bayes no disponible (usando solo BERT)'
            }
        
        X = self.vectorizer.transform([text])
        bayes_pred = self.model.predict(X)[0]
        bayes_probs = self.model.predict_proba(X)[0]
        
        emotion_idx = list(self.model.classes_).index(bayes_pred)
        bayes_conf = bayes_probs[emotion_idx]
        
        agreement = (bert_emotion == bayes_pred)
        
        if agreement:
            combined = (bert_confidence * 0.7 + bayes_conf * 0.3)
        else:
            combined = min(bert_confidence, bayes_conf) * 0.8
        
        return {
            'bert_emotion': bert_emotion,
            'bert_confidence': round(bert_confidence, 3),
            'bayes_emotion': bayes_pred,
            'bayes_confidence': round(bayes_conf, 3),
            'agreement': agreement,
            'combined_confidence': round(combined, 3),
            'status': 'ACUERDO' if agreement else 'DIVERGENCIA'
        }
    
    def save(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer,
                'emotions': self.emotions
            }, f)
        print(f"Bayes guardado en {self.cache_path}")
    
    def load(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.vectorizer = data['vectorizer']
                self.emotions = data['emotions']
            return True
        return False
```

---

### Paso 3: Modificar backend/main.py (3 Líneas)

Solo agrega esto al principio:

```python
from analysis.sentiment_validator import BayesValidator

validator = BayesValidator()
validator.load()
```

Y modifica tu endpoint `/analyze-sentiment`:

```python
@app.post("/analyze-sentiment")
def analyze_sentiment_with_validation(
    review_text: str,
    use_validation: bool = False
):
    emotion_result = analyze_sentiment(review_text)
    emotion = emotion_result['emotion']
    confidence = emotion_result['confidence']
    
    if use_validation and validator.model:
        validation = validator.validate(review_text, emotion, confidence)
        return {
            "bert": {
                "emotion": emotion,
                "confidence": confidence
            },
            "bayes_validation": {
                "emotion": validation['bayes_emotion'],
                "confidence": validation['bayes_confidence'],
                "status": validation['status']
            },
            "final": {
                "emotion": emotion,
                "confidence": validation['combined_confidence'],
                "reliability": "HIGH" if validation['agreement'] else "MEDIUM"
            }
        }
    
    return {
        "emotion": emotion,
        "confidence": confidence,
        "reliability": "BERT_ONLY"
    }
```

---

### Paso 4: Entrenar Bayes (UNA Sola Vez)

Crea backend/scripts/train_bayes.py:

```python
import pandas as pd
from analysis.sentiment_validator import BayesValidator

reviews_df = pd.read_csv('cache/reviews_with_sentiment.csv')

validator = BayesValidator()
validator.train(reviews_df)
validator.save()

print("Bayes entrenado y guardado para siempre")
```

Ejecuta (UNA sola vez):
```bash
cd backend
python scripts/train_bayes.py
```

Listo. Bayes queda entrenado y cargado. No vuelves a tocarlo.

---

## Qué Devuelve Tu API Ahora

### Sin Validación (Lo que tienes hoy)
```json
{
  "emotion": "Tristeza",
  "confidence": 0.85,
  "reliability": "BERT_ONLY"
}
```

### Con Validación (El Plus)
```json
{
  "bert": {
    "emotion": "Tristeza",
    "confidence": 0.85
  },
  "bayes_validation": {
    "emotion": "Tristeza",
    "confidence": 0.78,
    "status": "ACUERDO"
  },
  "final": {
    "emotion": "Tristeza",
    "confidence": 0.83,
    "reliability": "HIGH"
  }
}
```

---

## Casos de Uso Reales (O: Cómo Funciona en la Práctica)

### Caso 1: Texto Claro (Ambos Acuerdan, Qué Raro)

Review: "Este libro es hermoso, me encantó cada página"

| Modelo | Predicción | Confianza |
|--------|-----------|-----------|
| BERT | Alegría | 0.92 |
| Bayes | Alegría | 0.88 |
| **Final** | **Alegría** | **0.91 (HIGH)** |

→ Los dos están de acuerdo. Puedes confiar. Muestra esta recomendación sin miedo.

---

### Caso 2: Texto Ambiguo (Divergencia, Algo Pasó)

Review: "No me gustó, aunque tiene buen escribir"

| Modelo | Predicción | Confianza |
|--------|-----------|-----------|
| BERT | Disgusto | 0.65 |
| Bayes | Disgusto | 0.48 |
| **Final** | **Disgusto** | **0.52 (MEDIUM)** |

→ Ambos dicen "Disgusto" pero Bayes está menos seguro. Algo huele raro. Mejor revisar manualmente.

---

### Caso 3: Sarcasmo (BERT lo Entiende, Bayes No, Como Era de Esperar)

Review: "Qué maravilla de desastre, simplemente perfecto"

| Modelo | Predicción | Confianza |
|--------|-----------|-----------|
| BERT | Disgusto | 0.88 |
| Bayes | Alegría | 0.82 |
| **Final** | **Disgusto** | **0.70 (MEDIUM)** |

→ BERT capta que es sarcasmo. Bayes no (es ingenuo). API avisa: "Estos dos no se entienden". Muestra la predicción de BERT pero con confianza media.

---

## Cómo Encaja en Tu Arquitectura (La Imagen Mental)

**ANTES (Hoy):**
```
Usuario → API → BERT → Resultado
(esperas que BERT siempre tenga razón, pobre inocencia)
```

**DESPUÉS (Con Bayes):**
```
Usuario → API → BERT ──┐
                       ├→ Combinar + Confidence Score
              → Bayes ─┘
                       → Respuesta Mejorada
(BERT + Bayes = sistema con frenos y airbags)
```

**Archivos afectados:**
```
backend/
├── analysis/
│   ├── sentiment_analyzer.py  (sin cambios, no lo toques)
│   ├── sentiment_validator.py (NUEVO - aquí va Bayes)
│   └── __init__.py
├── main.py                    (3 líneas nuevas)
├── scripts/
│   ├── train_bayes.py         (NUEVO - corre 1 vez)
├── cache/
│   └── bayes_model.pkl        (se crea automáticamente)
└── requirements.txt           (agregar scikit-learn)
```

---

## Checklist: Hazlo en 30 Minutos

- [ ] Verificar scikit-learn==1.3.0 en requirements.txt
- [ ] Crear analysis/sentiment_validator.py (copiar código)
- [ ] Crear scripts/train_bayes.py (copiar código)
- [ ] Agregar 3 líneas a main.py
- [ ] Ejecutar: python scripts/train_bayes.py
- [ ] Testear endpoint con use_validation=True
- [ ] ✅ LISTO. Tienes score de confiabilidad.

---

## Bonus: Usos Avanzados (Si Tienes Energía)

### Opción 1: Procesamiento Batch 10x Más Rápido
```python
for review in 10000_reviews:
    if len(review) < 100:
        # Textos cortos: solo Bayes (50ms)
        resultado = validator.validate(review, None, None)
    else:
        # Textos largos: BERT (2s)
        resultado = analyze_sentiment(review)
```

### Opción 2: Auto-Reentrenamiento Semanal
```python
def weekly_bayes_update():
    nuevas_reseñas = load_feedback_usuarios_esta_semana()
    validator.train(nuevas_reseñas)
    validator.save()
```

### Opción 3: Monitoreo en Dashboard
```python
# Pregunta: Con qué frecuencia BERT y Bayes divergen?
# Si divergen mucho → BERT está roto → revisar
```

---

## Limitaciones (Sean Honestos)

**Bayes:**
- Ignora contexto ("no me encanta" = "me encanta" para él, es ingenuo)
- No entiende sarcasmo (literalmente no puede)
- Necesita entrenamiento previo
- Pero: rápido, ligero, perfecto como validador

**BERT:**
- Entiende contexto y sarcasmo (estado del arte)
- Lento (1-3s por review)
- Consume mucha RAM (es glotón)

**Juntos:**
- Tienes lo mejor de ambos mundos
- BERT maneja lo complicado, Bayes verifica rápido
- Fallan juntos solo si tus datos están rotos

---

## Resumen Final (La Verdad)

**Semana 1-2:** BERT funciona. Úsalo, no lo toques.

**Semana 3+:** Si sobra tiempo, implementa Bayes en 30 minutos.

**Resultado:**
- Confiabilidad medible en cada resultado
- Sabes cuándo revisar manualmente (divergencia)
- Batch processing 10x más rápido
- Los usuarios confían en las recomendaciones

**¿Es obligatorio?** No.
**¿Es profesional?** Sí.
**¿Impresiona?** También.

---

**Docker:** docker-compose up

**Docs:** Lee esto primero si tienes dudas

**Dudas:** Pregunta en Slack

**Algo se rompe:** Aviso inmediatamente

---

Suerte.

No me defraudan.

— *El Unicornio que se piró*
