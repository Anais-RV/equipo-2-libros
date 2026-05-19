import pandas as pd
import joblib
import os
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

# ============================================
# CONFIGURACIÓN
# ============================================

BASE_PATH = os.path.dirname(__file__)

DATASET_PATH = os.path.join(
    BASE_PATH,
    "dataset_para_analisis_sentimientos.csv"
)

MODEL_PATH = os.path.join(
    BASE_PATH,
    "modelo_hibrido_libros.pkl"
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
# CARGA GLOBAL (solo una vez)
# ============================================

df = pd.read_csv(DATASET_PATH)
df.columns = df.columns.str.lower()

modelo_generos = joblib.load(MODEL_PATH)
modelo_sentimientos = joblib.load(SENTIMENT_MODEL_PATH)
vectorizador_sentimientos = joblib.load(VECTORIZER_PATH)

# ============================================
# HELPERS
# ============================================

def get_book(book_title: str):
    """
    Busca un libro ignorando mayúsculas/minúsculas.
    """

    result = df[
        df["book_title"].str.lower() == book_title.lower()
    ]

    if result.empty:
        raise ValueError(f"No se encontró '{book_title}'")

    return result.iloc[0]


def calculate_similarity(
    target_genre,
    target_sentiment,
    row,
    sentiment_weight=1.0
):
    """
    Calcula score híbrido.
    """

    score = 0

    # Peso por género
    if row["main_genre"] == target_genre:
        score += 0.5

    # Peso por sentimiento
    if row["sentimiento_etiqueta"] == target_sentiment:
        score += 0.5 * sentiment_weight

    return score


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def find_similar_books(
    book_title: str,
    num_recommendations: int = 5,
    sentiment_weight: float = 1.0
) -> Dict[str, List[Dict]]:

    # ============================================
    # 1. BUSCAR LIBRO
    # ============================================

    target_book = get_book(book_title)

    sinopsis = str(target_book["book_details"])
    rating = float(target_book["review_rating"])

    # ============================================
    # 2. PREDECIR GÉNERO
    # ============================================

    entrada_genero = pd.DataFrame({
        "book_details": [sinopsis],
        "review_rating": [rating]
    })

    genero_predicho = modelo_generos.predict(
        entrada_genero
    )[0]

    # ============================================
    # 3. PREDECIR SENTIMIENTO
    # ============================================

    texto_tfidf = vectorizador_sentimientos.transform(
        [sinopsis]
    )

    sentimiento_predicho = modelo_sentimientos.predict(
        texto_tfidf
    )[0]

    # ============================================
    # 4. FILTRAR CANDIDATOS
    # ============================================

    candidatos = df[
        df["book_title"].str.lower() != book_title.lower()
    ].copy()

    # ============================================
    # 5. CALCULAR SCORES
    # ============================================

    candidatos["score"] = candidatos.apply(
        lambda row: calculate_similarity(
            genero_predicho,
            sentimiento_predicho,
            row,
            sentiment_weight
        ),
        axis=1
    )

    candidatos = candidatos.sort_values(
        by="score",
        ascending=False
    ).head(num_recommendations)

    # ============================================
    # 6. FORMATEAR RESPUESTA
    # ============================================

    recommendations = []

    for _, row in candidatos.iterrows():

        recommendations.append({
            "title": row["book_title"],
            "author": row.get("author", "Unknown"),
            "sentiment_score": round(float(row["score"]), 2),
            "reason": (
                f"Comparte el género '{genero_predicho}' "
                f"y una atmósfera emocional '{sentimiento_predicho}'."
            )
        })

    # IMPORTANTE:
    # este formato encaja con tu main.py

    return {
        "continuidad_saga": [],
        "libros_similares": recommendations
    }