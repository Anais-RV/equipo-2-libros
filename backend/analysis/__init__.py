"""
🦄 Análisis de Sentimientos - Sistema de Recomendación de Libros

Módulos del backend para análisis ML y recomendaciones.

Estructura:
- sentiment_analyzer_bert.py  → BERT + análisis de emociones
- recommender_bert.py        → BERT + cosine similarity
- data_processor.py     → Carga y limpieza de datos
- cache_manager.py      → Persistencia de resultados
"""

from .sentiment_analyzer_bert import analyze_sentiment
from .recommender_bert import find_similar_books
from .data_processor import load_dataset, preprocess_reviews
from .cache_manager import CacheManager

__all__ = [
    'analyze_sentiment',
    'find_similar_books',
    'load_dataset',
    'preprocess_reviews',
    'CacheManager'
]
