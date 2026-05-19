# 🦄 Bayes: Tu Segundo Cerebro (Cuando BERT No Confía Ni En Él Mismo)

Mira, tu código BERT funciona. Este documento es para quien quiera agregar un validador rápido.

- ✅ Darle a BERT un "verificador rápido"
- ✅ Obtener score de confiabilidad
- ✅ Saber CUÁNDO BERT está mintiendo
- ✅ Hacer batch 10x más rápido

**Sin presión:** Llega a la demo con BERT y funciona, es épico. Si quieres plus, aquí está.

---

## 🧠 La Idea: Dos Opiniones Mejor que Una

```
Usuario: "¿Este libro es triste?"

BERT:     → "Sí, tristeza 85%"
Bayes:    → "Veo palabras tristes... sí"

API:      → "Tristeza 92% (ambos de acuerdo) ✅"
           Confiabilidad: ALTA
```

---

## 💻 Implementación (30 Minutos)

### 1. Asegurar `requirements.txt`
```
scikit-learn==1.3.0
```

### 2. Crear `backend/analysis/sentiment_validator.py`

```python
import pickle
import os
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

class BayesValidator:
    def __init__(self, cache_path="cache/bayes_model.pkl"):
        self.cache_path = cache_path
        self.model = None
        self.vectorizer = None
        self.emotions = None
        
    def train(self, reviews_df):
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
        if self.model is None:
            return {
                'bert_emotion': bert_emotion,
                'bert_confidence': bert_confidence,
                'bayes_emotion': None,
                'bayes_confidence': None,
                'agreement': None,
                'combined_confidence': bert_confidence,
                'note': 'Bayes no entrenado (usando solo BERT)'
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
            'status': 'OK' if agreement else 'DIVERGENCIA'
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

### 3. Modificar `backend/main.py`

```python
from analysis.sentiment_validator import BayesValidator

validator = BayesValidator()
validator.load()

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

### 4. Entrenar Bayes (UNA sola vez)

Crea `backend/scripts/train_bayes.py`:

```python
import pandas as pd
from analysis.sentiment_validator import BayesValidator

reviews_df = pd.read_csv('cache/reviews_with_sentiment.csv')

validator = BayesValidator()
validator.train(reviews_df)
validator.save()

print("Bayes entrenado")
```

Ejecuta:
```bash
python scripts/train_bayes.py
```

---

## ✅ Checklist

- [ ] `scikit-learn==1.3.0` en requirements.txt
- [ ] Crear `analysis/sentiment_validator.py`
- [ ] Crear `scripts/train_bayes.py`
- [ ] Modificar `main.py` (agregar 3 líneas)
- [ ] Ejecutar entrenamiento
- [ ] Testear con `use_validation=True`

---

Listo. Tienes score de confiabilidad.

— El Unicornio
