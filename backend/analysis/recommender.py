"""
🦄 Recommender - Motor de "libros parecidos" y Sagas literarias

Una vez que sabes qué emociones genera un libro,
busca otros 5 libros que generen CASI LAS MISMAS emociones.

Algoritmo básico:
1. Cargar perfiles de los libros (pre-calculados desde el caché)
2. Calcular qué tan parecido es cada uno al que buscas (cosine similarity)
3. Retornar los TOP 5 más parecidos e inyectar lógica de continuidad de sagas.
"""

from sentiment_analyzer import analyze_sentiment
import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import os
import json

# Importamos tu CacheManager para conectar las piezas de forma directa
from cache_manager import CacheManager

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
    Carga perfiles emocionales desde el caché binario (.pkl).
    Si no existe, busca el CSV de perfiles dentro de la carpeta cache.
    """
    cache = CacheManager()
    all_profiles = cache.load_emotion_profiles()
    
    # Si el archivo .pkl no existe por algún motivo, buscamos el CSV de perfiles en la carpeta cache
    if all_profiles is None:
        CACHE_DIR = os.path.join(os.path.dirname(__file__), '../../cache')
        csv_path = os.path.join(CACHE_DIR, "emotion_profiles.csv")
        
        print(f"⚠️ [ADVERTENCIA] No se encontró el archivo pkl. Intentando cargar desde {csv_path}...")
        
        if os.path.exists(csv_path):
            all_profiles = pd.read_csv(csv_path)
        else:
            raise FileNotFoundError("❌ Error crítico: No hay perfiles calculados en el caché. Corre primero el analizador.")
            
    return all_profiles


def normalize_profile(profile: Dict[str, float]) -> np.ndarray:
    """
    Normaliza un perfil emocional para cosine similarity garantizando un array bidimensional.
    """
    vector = np.array([profile[emotion] for emotion in EMOTIONS])
    magnitude = np.linalg.norm(vector)
    if magnitude == 0:
        return vector.reshape(1, -1)
    return (vector / magnitude).reshape(1, -1)

def find_similar_profiles(
    input_profile: Dict[str, float],
    all_profiles: pd.DataFrame,
    method: str = "cosine"
) -> np.ndarray:
    """
    Calcula similitud emocional entre el libro objetivo
    y todos los libros del catálogo.
    """

    input_vector = normalize_profile(input_profile)

    all_vectors = all_profiles[EMOTIONS].values

    if method == "cosine":

        similarities = cosine_similarity(
            input_vector,
            all_vectors
        )[0]

    else:

        distances = np.linalg.norm(
            all_vectors - input_vector,
            axis=1
        )

        similarities = 1 / (1 + distances)

    return similarities


def apply_clustering(
    all_profiles: pd.DataFrame,
    n_clusters: int = 5
) -> KMeans:
    """
    Agrupa los libros analizados en clusters basados en su atmósfera emocional predominante.
    """
    vectors = all_profiles[EMOTIONS].values
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(vectors)
    return kmeans


def rank_recommendations(
    similarities: np.ndarray,
    book_data: pd.DataFrame,
    target_title: str,
    top_n: int = 5
) -> List[Dict]:
    """
    Ordena los libros por afinidad emocional, descarta el libro original y formatea la salida.
    """
    df_temp = book_data.copy()
    df_temp['similarity'] = similarities
    
    # Filtrar para no recomendar el mismo libro que el usuario acaba de leer
    df_temp = df_temp[df_temp['book_title'].str.lower() != target_title.lower()]
    
    # Ordenar de mayor a menor similitud
    df_ranked = df_temp.sort_values(by='similarity', ascending=False).head(top_n)
    
    recommendations = []
    for _, row in df_ranked.iterrows():
        # Lógica de "motivo" dinámico según la emoción más fuerte detectada por Hartmann
        primary_emotion = row[EMOTIONS].astype(float).idxmax()
        
        recommendations.append({
            "title": row['book_title'],
            "author": row['author'],
            "sentiment_score": round(float(row['similarity']), 2),
            "reason": f"Muestra una atmósfera similar con un fuerte matiz de '{primary_emotion}'."
        })
        
    return recommendations


def check_saga_continuity(target_title: str, all_profiles: pd.DataFrame) -> List[Dict]:
    """
    Verifica si el libro pertenece a una saga y extrae los volúmenes posteriores correlativos.
    """
    continuidad = []
    book_match = all_profiles[all_profiles['book_title'].str.lower() == target_title.lower()]
    
    if not book_match.empty:
        row = book_match.iloc[0]
        saga_name = row.get('saga_name')
        volumen_actual = row.get('volume_number', 1)
        
        # Si tiene una saga asignada en los metadatos
        if pd.notna(saga_name) and saga_name != "":
            # Buscamos los libros hermanos de la misma saga que vayan después en el orden
            siguientes = all_profiles[
                (all_profiles['saga_name'] == saga_name) & 
                (all_profiles['volume_number'] > volumen_actual)
            ].sort_values(by='volume_number')
            
            for _, next_row in siguientes.iterrows():
                continuidad.append({
                    "title": next_row['book_title'],
                    "author": next_row['author'],
                    "type": "Continuidad de Saga",
                    "reason": f"Es el volumen {int(next_row['volume_number'])} de la saga '{saga_name}'."
                })
    return continuidad


# ============================================
# FUNCIÓN PRINCIPAL HÍBRIDA
# ============================================

def find_similar_books(
    book_title: str,
    num_recommendations: int = 5
) -> Dict[str, List[Dict]]:
    """
    Encuentra libros similares usando perfiles emocionales.
    Si el libro no está cacheado, llama automáticamente
    a sentiment_analyzer.analyze_sentiment().
    """

    print(f"🔮 [MOTOR] Generando recomendaciones para '{book_title}'")

    all_profiles = load_emotion_profiles()

    # ============================================
    # 1. Buscar libro en caché
    # ============================================

    target_book = all_profiles[
        all_profiles['book_title'].str.lower()
        == book_title.lower()
    ]

    # ============================================
    # 2. Si NO existe → analizar automáticamente
    # ============================================

    if target_book.empty:

        print(f"[ANALYZER] '{book_title}' no está cacheado.")
        print("[ANALYZER] Ejecutando sentiment_analyzer...")

        try:
            new_profile = analyze_sentiment(book_title)

            # Recargar caché actualizado
            all_profiles = load_emotion_profiles()

            target_book = all_profiles[
                all_profiles['book_title'].str.lower()
                == book_title.lower()
            ]

        except Exception as e:
            print(f"❌ Error analizando '{book_title}': {e}")

            return {
                "continuidad_saga": [],
                "libros_similares": []
            }

    # ============================================
    # 3. Obtener perfil emocional
    # ============================================

    sentiment_profile = target_book.iloc[0][EMOTIONS].to_dict()

    # ============================================
    # 4. Buscar continuidad de saga
    # ============================================

    saga_recommendations = check_saga_continuity(
        book_title,
        all_profiles
    )

    # ============================================
    # 5. Calcular similaridad
    # ============================================

    similarities = find_similar_profiles(
        sentiment_profile,
        all_profiles,
        method="cosine"
    )

    # ============================================
    # 6. Obtener TOP similares
    # ============================================

    similar_books = rank_recommendations(
        similarities,
        all_profiles,
        target_title=book_title,
        top_n=num_recommendations
    )

    # ============================================
    # 7. Resultado final
    # ============================================

    return {
        "continuidad_saga": saga_recommendations,
        "libros_similares": similar_books
    }

# ============================================
# DEBUGGING / TESTING
# ============================================

if __name__ == "__main__":
    # Generamos un entorno de test de simulación con datos reales de tu caché
    print("--- INICIANDO DIAGNÓSTICO DEL RECOMENDADOR ---")
    
    try:
        # Prueba simulando que el usuario introduce el volumen 1 de Harry Potter
        # (Asegúrate de escribir un título que ya esté procesado en tu JSON/PKL)
        test_title = "The War of Art: Winning the Inner Creative Battle"  # Cambia esto por un título que tengas en tu caché
        
        resultados = find_similar_books(test_title, num_recommendations=3)
        
        print("\n📦 CONTINUIDAD DE LA SAGA DETECTADA:")
        for b in resultados["continuidad_saga"]:
            print(f" ➡️ {b['title']} ({b['reason']})")
            
        print("\n🎯 LIBROS RECOMENDADOS POR AFINIDAD EMOCIONAL (COSINE SIMILARITY):")
        for b in resultados["libros_similares"]:
            print(f" ➡️ {b['title']} - Coincidencia: {int(b['sentiment_score']*100)}% ({b['reason']})")
            
    except Exception as e:
        print(f"❌ Error durante el test de integración: {e}")
        print("Asegúrate de que el analizador haya guardado al menos un lote de perfiles primero.")