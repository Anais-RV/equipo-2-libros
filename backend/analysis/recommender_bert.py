"""
🦄 Recommender - Motor de "libros parecidos"
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import os

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data')
EMOTIONS = ['joy', 'sadness', 'fear', 'surprise', 'anger', 'disgust']
TOP_N = 5

# ============================================
# FUNCIONES HELPER
# ============================================

def load_emotion_profiles() -> pd.DataFrame:
    """
    Carga perfiles emocionales pre-calculados.
    """
    possible_paths = [
        os.path.join(DATA_PATH, "emotion_profiles_60_books.csv"),
        os.path.join(os.getcwd(), "emotion_profiles_60_books.csv"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            profiles = pd.read_csv(path)
            print(f"Perfiles cargados desde: {path}")
            return profiles

    raise FileNotFoundError("No se encontró emotion_profiles_60_books.csv")


def normalize_profile(profile: Dict[str, float]) -> np.ndarray:
    """
    Normaliza un perfil emocional para cosine similarity.
    """
    vector = np.array([profile[emotion] for emotion in EMOTIONS])

    magnitude = np.linalg.norm(vector)

    if magnitude == 0:
        return vector

    return vector / magnitude


def find_similar_profiles(
    input_profile: Dict[str, float],
    all_profiles: pd.DataFrame,
    method: str = "cosine"
) -> np.ndarray:
    """
    Calcula similitud emocional entre un perfil y todos los demás.
    """
    input_vector = normalize_profile(input_profile)

    all_vectors = all_profiles[EMOTIONS].values

    similarities = cosine_similarity(
        [input_vector],
        all_vectors
    )[0]

    return similarities


def apply_clustering(
    all_profiles: pd.DataFrame,
    n_clusters: int = 10
) -> KMeans:
    """
    Agrupa libros similares en clusters.
    """
    vectors = all_profiles[EMOTIONS].values

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    kmeans.fit(vectors)

    return kmeans


def rank_recommendations(
    similarities: np.ndarray,
    book_data: pd.DataFrame,
    top_n: int = 5
) -> List[Dict]:
    """
    Ordena libros por similitud y retorna TOP N.
    """
    book_data = book_data.copy()
    book_data["similarity"] = similarities

    ranked_books = book_data.sort_values(
        "similarity",
        ascending=False
    )

    recommendations = []

    for _, row in ranked_books.head(top_n).iterrows():
        recommendations.append({
            "title": row["book_title"],
            "author": row["author"],
            "sentiment_score": round(float(row["similarity"]), 4),
            "reason": "Similar emotional profile"
        })

    return recommendations


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def find_similar_books(
    sentiment_profile: Dict[str, float],
    num_recommendations: int = 5
) -> List[Dict]:
    """
    Encuentra los TOP libros más parecidos emocionalmente.
    """
    print("[RECOMMENDER] Encontrando libros similares...")

    all_profiles = load_emotion_profiles()

    similarities = find_similar_profiles(
        sentiment_profile,
        all_profiles
    )

    recommendations = rank_recommendations(
        similarities,
        all_profiles,
        num_recommendations
    )

    return recommendations


# ============================================
# DEBUGGING / TESTING
# ============================================

if __name__ == "__main__":
    test_profile = {
        "joy": 0.75,
        "sadness": 0.2,
        "fear": 0.1,
        "surprise": 0.65,
        "anger": 0.05,
        "disgust": 0.08,
    }

    recommendations = find_similar_books(
        test_profile,
        num_recommendations=5
    )

    print("Recomendaciones:")
    print(recommendations)