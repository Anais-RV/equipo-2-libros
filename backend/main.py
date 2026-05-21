from pathlib import Path
import sys
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent          # /app/backend
ROOT_DIR = BASE_DIR.parent                          # /app
DATA_DIR = ROOT_DIR / "data"                        # /app/data

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


# ============================================================
# IMPORTS DEL RECOMENDADOR
# ============================================================

try:
    from analysis.recommender import (
        recomendar_por_afinidad_emocional,
        find_similar_books,
    )
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "No se pudo importar analysis.recommender. "
        "Comprueba que existe /app/backend/analysis/recommender.py "
        "y también /app/backend/analysis/__init__.py"
    ) from error


# ============================================================
# ARCHIVOS CSV
# ============================================================

BOOKS_PATH = DATA_DIR / "books_clean.csv"
PROFILES_PATH = DATA_DIR / "emotion_profiles.csv"
RECOMMENDATIONS_PATH = DATA_DIR / "all_book_recommendations.csv"


# ============================================================
# APP FASTAPI
# ============================================================

app = FastAPI(
    title="API Recomendador de Libros",
    description="API para buscar libros y recomendar por afinidad emocional.",
    version="3.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes poner solo la URL de React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CACHE EN MEMORIA
# ============================================================

books_df = None
profiles_df = None
recommendations_df = None


def cargar_csv_seguro(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    return pd.read_csv(path)


def get_books_df() -> pd.DataFrame:
    global books_df

    if books_df is None:
        books_df = cargar_csv_seguro(BOOKS_PATH)

    return books_df


def get_profiles_df() -> pd.DataFrame:
    global profiles_df

    if profiles_df is None:
        profiles_df = cargar_csv_seguro(PROFILES_PATH)

    return profiles_df


def get_recommendations_df() -> pd.DataFrame:
    global recommendations_df

    if recommendations_df is None:
        recommendations_df = cargar_csv_seguro(RECOMMENDATIONS_PATH)

    return recommendations_df


def limpiar_nan(valor):
    if pd.isna(valor):
        return None

    if hasattr(valor, "item"):
        return valor.item()

    return valor


def fila_a_dict(fila) -> dict:
    resultado = {}

    for columna, valor in fila.items():
        resultado[columna] = limpiar_nan(valor)

    return resultado


def normalizar_texto(texto) -> str:
    if texto is None:
        return ""

    return str(texto).lower().strip()


# ============================================================
# HOME / HEALTH
# ============================================================

@app.get("/")
def home():
    return {
        "message": "API de recomendación de libros funcionando correctamente",
        "version": "3.0.0",
        "mode": "emotion_profiles.csv",
        "endpoints": {
            "health": "/health",
            "books": "/books",
            "book_detail": "/books/{book_id}",
            "search": "/search?title=harry",
            "profiles": "/profiles",
            "profile_detail": "/profiles/{book_id}",
            "recommend_emotional": "/recommendations/emotional?title=Harry Potter and the Half-Blood Prince",
            "recommend_compat": "/recommend?title=Harry Potter and the Half-Blood Prince",
            "recommend_precomputed": "/recommendations/precomputed?title=Harry Potter",
            "reload": "/reload",
        },
    }


@app.get("/health")
def health_check():
    return {
        "api": "ok",
        "data_dir": str(DATA_DIR),
        "books_clean.csv": BOOKS_PATH.exists(),
        "emotion_profiles.csv": PROFILES_PATH.exists(),
        "all_book_recommendations.csv": RECOMMENDATIONS_PATH.exists(),
        "books_path": str(BOOKS_PATH),
        "profiles_path": str(PROFILES_PATH),
        "recommendations_path": str(RECOMMENDATIONS_PATH),
    }


# ============================================================
# BOOKS
# ============================================================

@app.get("/books")
def listar_libros(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    try:
        df = get_books_df()

        total = len(df)
        resultados = df.iloc[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "books": [
                fila_a_dict(fila)
                for _, fila in resultados.iterrows()
            ],
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/books/{book_id}")
def obtener_libro(book_id: str):
    try:
        df = get_books_df()

        if "book_id" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="books_clean.csv no tiene columna book_id",
            )

        df = df.copy()
        df["book_id"] = df["book_id"].astype(str)

        resultado = df[df["book_id"] == str(book_id)]

        if resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el libro con book_id: {book_id}",
            )

        return fila_a_dict(resultado.iloc[0])

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/search")
def buscar_libros(
    title: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    try:
        df = get_books_df()

        if "book_title" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="books_clean.csv no tiene columna book_title",
            )

        df = df.copy()
        df["book_title"] = df["book_title"].fillna("").astype(str)

        resultados = df[
            df["book_title"].str.lower().str.contains(
                title.lower(),
                na=False,
                regex=False,
            )
        ].head(limit)

        return {
            "query": title,
            "total": len(resultados),
            "books": [
                fila_a_dict(fila)
                for _, fila in resultados.iterrows()
            ],
        }

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# EMOTION PROFILES
# ============================================================

@app.get("/profiles")
def listar_perfiles(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    try:
        df = get_profiles_df()

        total = len(df)
        resultados = df.iloc[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "profiles": [
                fila_a_dict(fila)
                for _, fila in resultados.iterrows()
            ],
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/profiles/{book_id}")
def obtener_perfil_libro(book_id: str):
    try:
        df = get_profiles_df()

        if "book_id" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="emotion_profiles.csv no tiene columna book_id",
            )

        df = df.copy()
        df["book_id"] = df["book_id"].astype(str)

        resultado = df[df["book_id"] == str(book_id)]

        if resultado.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró perfil emocional para book_id: {book_id}",
            )

        return fila_a_dict(resultado.iloc[0])

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/profiles/search/by-title")
def buscar_perfil_por_titulo(
    title: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    try:
        df = get_profiles_df()

        if "book_title" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="emotion_profiles.csv no tiene columna book_title",
            )

        df = df.copy()
        df["book_title"] = df["book_title"].fillna("").astype(str)

        resultados = df[
            df["book_title"].str.lower().str.contains(
                title.lower(),
                na=False,
                regex=False,
            )
        ].head(limit)

        return {
            "query": title,
            "total": len(resultados),
            "profiles": [
                fila_a_dict(fila)
                for _, fila in resultados.iterrows()
            ],
        }

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# RECOMENDACIONES EN TIEMPO REAL
# ============================================================

@app.get("/recommendations/emotional")
def recomendar_emocional(
    title: str = Query(..., min_length=1),
    top_n: int = Query(default=5, ge=1, le=20),
    min_reviews: int = Query(default=1, ge=1),
    excluir_mismo_autor: bool = Query(default=False),
):
    """
    Recomendación usando emotion_profiles.csv.
    No recalcula BERT ni lee reviews.
    """
    try:
        resultado = recomendar_por_afinidad_emocional(
            titulo_libro=title,
            top_n=top_n,
            min_reviews=min_reviews,
            excluir_mismo_autor=excluir_mismo_autor,
        )

        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)

        return resultado

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/recommend")
def recomendar_compatibilidad(
    title: str = Query(..., min_length=1),
    num_recommendations: int = Query(default=5, ge=1, le=20),
):
    """
    Endpoint compatible con versiones anteriores.
    """
    try:
        resultado = find_similar_books(
            title=title,
            num_recommendations=num_recommendations,
        )

        return resultado

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# RECOMENDACIONES PRECALCULADAS
# ============================================================

@app.get("/recommendations/precomputed")
def recomendaciones_precalculadas(
    book_id: Optional[str] = Query(default=None),
    title: Optional[str] = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
):
    """
    Lee all_book_recommendations.csv generado por recommender.py.
    """
    try:
        df = get_recommendations_df()
        df = df.copy()

        if book_id is not None:
            if "book_id" not in df.columns:
                raise HTTPException(
                    status_code=500,
                    detail="all_book_recommendations.csv no tiene columna book_id",
                )

            df["book_id"] = df["book_id"].astype(str)
            df = df[df["book_id"] == str(book_id)]

        elif title is not None:
            if "book_title" not in df.columns:
                raise HTTPException(
                    status_code=500,
                    detail="all_book_recommendations.csv no tiene columna book_title",
                )

            df["book_title"] = df["book_title"].fillna("").astype(str)
            df = df[
                df["book_title"].str.lower().str.contains(
                    title.lower(),
                    na=False,
                    regex=False,
                )
            ]

        else:
            raise HTTPException(
                status_code=400,
                detail="Debes enviar book_id o title",
            )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron recomendaciones precalculadas",
            )

        if "recommended_rank" in df.columns:
            df = df.sort_values("recommended_rank")

        df = df.head(limit)

        return {
            "total": len(df),
            "recommendations": [
                fila_a_dict(fila)
                for _, fila in df.iterrows()
            ],
        }

    except HTTPException:
        raise

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# RECARGAR CSV
# ============================================================

@app.post("/reload")
def recargar_datos():
    """
    Limpia la caché en memoria.
    Útil después de cambiar CSVs.
    """
    global books_df, profiles_df, recommendations_df

    books_df = None
    profiles_df = None
    recommendations_df = None

    return {
        "message": "Datos recargados correctamente",
        "books_clean.csv": BOOKS_PATH.exists(),
        "emotion_profiles.csv": PROFILES_PATH.exists(),
        "all_book_recommendations.csv": RECOMMENDATIONS_PATH.exists(),
    }


# ============================================================
# EJECUCIÓN DIRECTA OPCIONAL
# ============================================================



  
if __name__ == "__main__":
    import uvicorn

    logger.info("Iniciando API de Recomendación de Libros...")
    logger.info("Frontend: http://localhost:3000")
    logger.info("API: http://localhost:8000")
    logger.info("Docs: http://localhost:8000/docs") 