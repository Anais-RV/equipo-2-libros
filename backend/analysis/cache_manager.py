from pathlib import Path
from datetime import datetime, timezone
import hashlib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
DATA_DIR = ROOT_DIR / "data"

CACHE_PATH = DATA_DIR / "sentiment_cache.csv"

# Cambia esto cuando cambies de modelo, reglas, texto usado o estrategia.
MODEL_VERSION = "roberta_review_only_v1"

CACHE_COLUMNS = [
    "text_hash",
    "model_version",
    "sentimiento",
    "sentimiento_modelo",
    "score",
    "prob_negativo",
    "prob_neutral",
    "prob_positivo",
    "created_at",
]


def normalizar_texto_cache(texto):
    if texto is None:
        return ""

    texto = str(texto)
    texto = texto.replace("\n", " ").replace("\r", " ")
    texto = " ".join(texto.split())
    texto = texto.strip()

    return texto


def calcular_hash_texto(texto, model_version=MODEL_VERSION):
    texto = normalizar_texto_cache(texto)
    contenido = f"{model_version}::{texto}"
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def crear_cache_vacia():
    return pd.DataFrame(columns=CACHE_COLUMNS)


def cargar_cache_sentimientos():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CACHE_PATH.exists():
        return crear_cache_vacia()

    try:
        cache_df = pd.read_csv(CACHE_PATH)

        for columna in CACHE_COLUMNS:
            if columna not in cache_df.columns:
                cache_df[columna] = None

        cache_df = cache_df[CACHE_COLUMNS].copy()
        cache_df["text_hash"] = cache_df["text_hash"].astype(str)
        cache_df["model_version"] = cache_df["model_version"].astype(str)

        return cache_df

    except Exception as error:
        print(f"⚠️ No se pudo cargar la caché. Se creará una nueva. Error: {error}")
        return crear_cache_vacia()


def guardar_cache_sentimientos(cache_df):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if cache_df is None or cache_df.empty:
        crear_cache_vacia().to_csv(CACHE_PATH, index=False)
        return

    cache_df = cache_df.copy()

    for columna in CACHE_COLUMNS:
        if columna not in cache_df.columns:
            cache_df[columna] = None

    cache_df = cache_df[CACHE_COLUMNS]
    cache_df = cache_df.drop_duplicates(
        subset=["text_hash", "model_version"],
        keep="last",
    )

    cache_df.to_csv(CACHE_PATH, index=False)


def obtener_prediccion_cache(texto, cache_df, model_version=MODEL_VERSION):
    if cache_df is None or cache_df.empty:
        return None

    text_hash = calcular_hash_texto(texto, model_version=model_version)

    fila = cache_df[
        (cache_df["text_hash"].astype(str) == text_hash)
        & (cache_df["model_version"].astype(str) == str(model_version))
    ]

    if fila.empty:
        return None

    registro = fila.iloc[-1].to_dict()

    return {
        "sentimiento": registro.get("sentimiento"),
        "sentimiento_modelo": registro.get("sentimiento_modelo"),
        "score": float(registro.get("score", 0.0) or 0.0),
        "probabilidades": {
            "Negativo": float(registro.get("prob_negativo", 0.0) or 0.0),
            "Neutral": float(registro.get("prob_neutral", 0.0) or 0.0),
            "Positivo": float(registro.get("prob_positivo", 0.0) or 0.0),
        },
    }


def obtener_sentimiento_cache(texto, cache_df, model_version=MODEL_VERSION):
    """
    Compatibilidad con código antiguo.
    """
    prediccion = obtener_prediccion_cache(texto, cache_df, model_version)

    if prediccion is None:
        return None

    return prediccion["sentimiento"]


def agregar_prediccion_cache(texto, resultado, cache_df, model_version=MODEL_VERSION):
    if cache_df is None:
        cache_df = crear_cache_vacia()

    probabilidades = resultado.get("probabilidades", {}) or {}

    nuevo_registro = {
        "text_hash": calcular_hash_texto(texto, model_version=model_version),
        "model_version": model_version,
        "sentimiento": resultado.get("sentimiento", "Neutral"),
        "sentimiento_modelo": resultado.get("sentimiento_modelo", resultado.get("sentimiento", "Neutral")),
        "score": float(resultado.get("score", 0.0) or 0.0),
        "prob_negativo": float(probabilidades.get("Negativo", 0.0) or 0.0),
        "prob_neutral": float(probabilidades.get("Neutral", 0.0) or 0.0),
        "prob_positivo": float(probabilidades.get("Positivo", 0.0) or 0.0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    cache_df = pd.concat(
        [cache_df, pd.DataFrame([nuevo_registro])],
        ignore_index=True,
    )

    cache_df = cache_df.drop_duplicates(
        subset=["text_hash", "model_version"],
        keep="last",
    )

    return cache_df


def agregar_sentimiento_cache(
    texto,
    sentimiento,
    cache_df,
    model_version=MODEL_VERSION,
    score=0.0,
    sentimiento_modelo=None,
    probabilidades=None,
):
    """
    Compatibilidad con código antiguo.
    """
    resultado = {
        "sentimiento": sentimiento,
        "sentimiento_modelo": sentimiento_modelo or sentimiento,
        "score": score,
        "probabilidades": probabilidades
        or {
            "Negativo": 0.0,
            "Neutral": 0.0,
            "Positivo": 0.0,
        },
    }

    return agregar_prediccion_cache(texto, resultado, cache_df, model_version)
