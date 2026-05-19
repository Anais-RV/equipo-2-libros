"""
🦄 Sentiment Analyzer - El corazón del análisis
"""

import pandas as pd
from typing import Dict
import os
from transformers import pipeline

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data')

EMOTIONS = [
    'joy',
    'sadness',
    'fear',
    'surprise',
    'anger',
    'disgust'
]

# ============================================
# FUNCIONES HELPER
# ============================================

def load_book_reviews(book_title: str) -> pd.DataFrame:
    """
    Carga las reviews de un libro específico.
    """

    books_path = os.path.join(DATA_PATH, "books_clean.csv")
    reviews_path = os.path.join(DATA_PATH, "reviews_clean.csv")

    books_df = pd.read_csv(books_path)
    reviews_df = pd.read_csv(reviews_path)

    # Buscar libro ignorando mayúsculas/minúsculas
    book_match = books_df[
        books_df["book_title"].str.lower() == book_title.lower()
    ]

    if book_match.empty:
        raise ValueError(
            f"No se encontró el libro: {book_title}"
        )

    # Obtener book_id
    book_id = book_match.iloc[0]["book_id"]

    # Filtrar reviews del libro
    book_reviews = reviews_df[
        reviews_df["book_id"] == book_id
    ]

    if book_reviews.empty:
        raise ValueError(
            f"No hay reviews para el libro: {book_title}"
        )

    return book_reviews


def apply_bert_to_reviews(
    reviews: pd.Series
) -> pd.DataFrame:
    """
    Aplica BERT para detectar emociones.
    """

    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

    results = []

    # Limitar reviews para pruebas iniciales
    for review in reviews.head(5):

        if (
            not isinstance(review, str)
            or len(review.strip()) == 0
        ):
            continue

        result = classifier(
            review,
            candidate_labels=EMOTIONS
        )

        emotion_scores = dict(
            zip(
                result["labels"],
                result["scores"]
            )
        )

        results.append(emotion_scores)

    return pd.DataFrame(results)


def aggregate_emotion_scores(
    emotion_df: pd.DataFrame
) -> Dict[str, float]:
    """
    Agrega scores emocionales.
    """

    if emotion_df.empty:
        raise ValueError(
            "No emotion scores available"
        )

    profile = emotion_df[EMOTIONS].mean().to_dict()

    profile["average_sentiment"] = round(
        sum(profile.values()) / len(EMOTIONS),
        4
    )

    return profile


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================
def analyze_sentiment(
    book_title: str
) -> Dict[str, float]:
    """
    Analiza emociones de un libro usando semi-cache CSV.
    """

    cache_path = "emotion_profiles_30_books.csv"

    # ============================================
    # 1. Intentar cargar desde cache
    # ============================================

    if os.path.exists(cache_path):

        cache_df = pd.read_csv(cache_path)

        cached_book = cache_df[
            cache_df["book_title"].str.lower()
            == book_title.lower()
        ]

        if not cached_book.empty:

            print(f"[CACHE] Perfil encontrado para '{book_title}'")

            row = cached_book.iloc[0]

            return {
                "joy": row["joy"],
                "sadness": row["sadness"],
                "fear": row["fear"],
                "surprise": row["surprise"],
                "anger": row["anger"],
                "disgust": row["disgust"],
                "average_sentiment": row["average_sentiment"]
            }

    # ============================================
    # 2. Ejecutar BERT si no existe cache
    # ============================================

    print(f"[BERT] Analizando '{book_title}'")

    reviews = load_book_reviews(book_title)

    if len(reviews) < 1:
        raise ValueError(
            f"No hay suficientes reviews para: {book_title}"
        )

    emotion_scores = apply_bert_to_reviews(
        reviews["review_content"]
    )

    profile = aggregate_emotion_scores(
        emotion_scores
    )

    return profile

def analyze_first_60_books() -> pd.DataFrame:
    """
    Analiza sentimientos de los primeros 60 libros del CSV limpio.
    """

    books_path = os.path.join(DATA_PATH, "books_clean.csv")
    books_df = pd.read_csv(books_path)

    results = []

    for index, row in books_df.head(60).iterrows():
        title = row["book_title"]

        print(f"\n[{index + 1}/60] Analizando: {title}")

        try:
            profile = analyze_sentiment(title)

            result = {
                "book_id": row["book_id"],
                "book_title": title,
                "author": row["author"],
                **profile
            }

            results.append(result)

        except Exception as e:
            print(f"Error con '{title}': {e}")

    emotion_profiles = pd.DataFrame(results)

    emotion_profiles.to_csv(
        "emotion_profiles_60_books.csv",
        index=False
    )

    print("\nCSV generado: emotion_profiles_60_books.csv")

    return emotion_profiles

# ============================================
# DEBUGGING / TESTING
# ============================================

if __name__ == "__main__":
    profiles = analyze_first_60_books()

    print("\nPerfiles generados:")
    print(profiles.head())