import pandas as pd
import joblib
import os

# ============================================
# CONFIG
# ============================================

BASE_PATH = os.path.dirname(__file__)

DATASET_PATH = os.path.join(
    BASE_PATH,
    "dataset_para_analisis_sentimientos.csv"
)

SENTIMENT_MODEL_PATH = os.path.join(
    BASE_PATH,
    "clasificador_sentimientos.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_PATH,
    "vectorizador_sentimientos.pkl"
)

# ============================================
# LOAD
# ============================================

df = pd.read_csv(DATASET_PATH)
df.columns = df.columns.str.lower()

modelo_sentimientos = joblib.load(SENTIMENT_MODEL_PATH)
vectorizador_sentimientos = joblib.load(VECTORIZER_PATH)

# ============================================
# MAIN FUNCTION
# ============================================

def analyze_sentiment(book_title: str):

    result = df[
        df["book_title"].str.lower() == book_title.lower()
    ]

    if result.empty:
        raise ValueError(f"No se encontró '{book_title}'")

    libro = result.iloc[0]

    texto = str(libro["book_details"])

    texto_tfidf = vectorizador_sentimientos.transform(
        [texto]
    )

    sentimiento = modelo_sentimientos.predict(
        texto_tfidf
    )[0]

    return {
        "book_title": book_title,
        "sentiment": sentimiento
    }