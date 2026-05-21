from pathlib import Path
import sys
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from predictor_sentimientos import PredictorSentimientos
from cache_manager import (
    cargar_cache_sentimientos,
    guardar_cache_sentimientos,
    obtener_prediccion_cache,
    agregar_prediccion_cache,
    MODEL_VERSION,
)


ROOT_DIR = BASE_DIR.parent.parent
DATA_DIR = ROOT_DIR / "data"

DATASET_PATH = DATA_DIR / "dataset_bert_sentimientos.csv"
OUTPUT_PATH = DATA_DIR / "book_emotional_profiles.csv"

BATCH_SIZE = 64
GUARDAR_CACHE_CADA = 5000


def cargar_dataset():
    print("=== CARGANDO DATASET ===")
    print("Dataset:", DATASET_PATH)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"No existe el dataset: {DATASET_PATH}. "
            "Primero ejecuta preparar_dataset_bert.py"
        )

    df = pd.read_csv(DATASET_PATH)

    print("Registros cargados:", len(df))
    print("Columnas:", df.columns.tolist())

    return df


def validar_dataset(df):
    print("\n=== VALIDANDO DATASET ===")

    columnas_necesarias = [
        "book_id",
        "book_title",
        "texto_bert",
    ]

    for columna in columnas_necesarias:
        if columna not in df.columns:
            raise ValueError(f"Falta la columna obligatoria: {columna}")

    df = df.dropna(subset=columnas_necesarias).copy()

    df["book_id"] = df["book_id"].astype(str).str.strip()
    df["book_title"] = df["book_title"].astype(str).str.strip()
    df["texto_bert"] = df["texto_bert"].astype(str).str.strip()

    df = df[df["book_id"] != ""]
    df = df[df["book_title"] != ""]
    df = df[df["texto_bert"] != ""]

    # Evita recalcular reviews repetidas exactas del mismo libro.
    df = df.drop_duplicates(subset=["book_id", "texto_bert"]).copy()

    print("Registros válidos:", len(df))
    print("Libros únicos:", df["book_id"].nunique())

    return df


def resultado_neutral_por_error(texto):
    return {
        "texto": texto,
        "sentimiento": "Neutral",
        "sentimiento_modelo": "error_fallback",
        "score": 0.0,
        "probabilidades": {
            "Negativo": 0.0,
            "Neutral": 1.0,
            "Positivo": 0.0,
        },
    }


def predecir_sentimientos_con_cache(df, predictor):
    print("\n=== PREDICIENDO SENTIMIENTOS CON CACHÉ Y BATCH ===")
    print("Versión del modelo:", MODEL_VERSION)

    cache_df = cargar_cache_sentimientos()

    resultados_por_indice = {}
    textos_nuevos = []
    indices_nuevos = []

    cacheados = 0

    for indice, texto in df["texto_bert"].items():
        prediccion_cacheada = obtener_prediccion_cache(
            texto=texto,
            cache_df=cache_df,
            model_version=MODEL_VERSION,
        )

        if prediccion_cacheada is not None:
            resultados_por_indice[indice] = prediccion_cacheada
            cacheados += 1
        else:
            textos_nuevos.append(texto)
            indices_nuevos.append(indice)

    print("Predicciones encontradas en caché:", cacheados)
    print("Predicciones nuevas a calcular:", len(textos_nuevos))

    if textos_nuevos:
        total_nuevos = len(textos_nuevos)

        for inicio in range(0, total_nuevos, BATCH_SIZE):
            fin = inicio + BATCH_SIZE
            batch_textos = textos_nuevos[inicio:fin]
            batch_indices = indices_nuevos[inicio:fin]

            try:
                resultados_batch = predictor.predecir_lote(
                    textos=batch_textos,
                    batch_size=BATCH_SIZE,
                )
            except Exception as error:
                print(f"⚠️ Error en batch {inicio}-{fin}: {error}")
                resultados_batch = [
                    resultado_neutral_por_error(texto)
                    for texto in batch_textos
                ]

            for indice, texto, resultado in zip(batch_indices, batch_textos, resultados_batch):
                resultados_por_indice[indice] = resultado
                cache_df = agregar_prediccion_cache(
                    texto=texto,
                    resultado=resultado,
                    cache_df=cache_df,
                    model_version=MODEL_VERSION,
                )

            procesados = min(fin, total_nuevos)

            if procesados % 512 == 0 or procesados == total_nuevos:
                print(f"Predicciones nuevas procesadas: {procesados}/{total_nuevos}")

            if procesados % GUARDAR_CACHE_CADA == 0 or procesados == total_nuevos:
                guardar_cache_sentimientos(cache_df)
                print(f"Cache guardada: {procesados}/{total_nuevos}")

    sentimientos = []
    scores = []
    labels_modelo = []
    prob_negativo = []
    prob_neutral = []
    prob_positivo = []

    for indice in df.index:
        resultado = resultados_por_indice.get(indice)

        if resultado is None:
            resultado = resultado_neutral_por_error(df.loc[indice, "texto_bert"])

        probabilidades = resultado.get("probabilidades", {}) or {}

        sentimientos.append(resultado.get("sentimiento", "Neutral"))
        scores.append(float(resultado.get("score", 0.0) or 0.0))
        labels_modelo.append(resultado.get("sentimiento_modelo", resultado.get("sentimiento", "Neutral")))
        prob_negativo.append(float(probabilidades.get("Negativo", 0.0) or 0.0))
        prob_neutral.append(float(probabilidades.get("Neutral", 0.0) or 0.0))
        prob_positivo.append(float(probabilidades.get("Positivo", 0.0) or 0.0))

    df = df.copy()
    df["sentimiento_predicho"] = sentimientos
    df["sentimiento_score"] = scores
    df["sentimiento_modelo"] = labels_modelo
    df["prob_negativo"] = prob_negativo
    df["prob_neutral"] = prob_neutral
    df["prob_positivo"] = prob_positivo

    guardar_cache_sentimientos(cache_df)

    print("\nDistribución de sentimientos predichos:")
    print(df["sentimiento_predicho"].value_counts())

    print("\nScore medio:", round(df["sentimiento_score"].mean(), 4))

    return df


def crear_perfiles_emocionales(df):
    print("\n=== CREANDO PERFILES EMOCIONALES ===")

    columnas_extra = []

    for columna in ["author", "genres", "average_rating"]:
        if columna in df.columns:
            columnas_extra.append(columna)

    columnas_agrupacion = ["book_id", "book_title"] + columnas_extra

    conteo = (
        df.groupby(columnas_agrupacion + ["sentimiento_predicho"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for sentimiento in ["Negativo", "Neutral", "Positivo"]:
        if sentimiento not in conteo.columns:
            conteo[sentimiento] = 0

    metricas_modelo = (
        df.groupby(columnas_agrupacion)
        .agg(
            total_reviews=("texto_bert", "count"),
            score_medio=("sentimiento_score", "mean"),
            prob_negativo_media=("prob_negativo", "mean"),
            prob_neutral_media=("prob_neutral", "mean"),
            prob_positivo_media=("prob_positivo", "mean"),
        )
        .reset_index()
    )

    perfiles = conteo.merge(
        metricas_modelo,
        on=columnas_agrupacion,
        how="inner",
    )

    perfiles = perfiles[perfiles["total_reviews"] > 0].copy()

    perfiles["ratio_negativo"] = perfiles["Negativo"] / perfiles["total_reviews"]
    perfiles["ratio_neutral"] = perfiles["Neutral"] / perfiles["total_reviews"]
    perfiles["ratio_positivo"] = perfiles["Positivo"] / perfiles["total_reviews"]

    perfiles["sentimiento_dominante"] = perfiles[
        ["Negativo", "Neutral", "Positivo"]
    ].idxmax(axis=1)

    perfiles["score_medio"] = perfiles["score_medio"].round(4)
    perfiles["prob_negativo_media"] = perfiles["prob_negativo_media"].round(4)
    perfiles["prob_neutral_media"] = perfiles["prob_neutral_media"].round(4)
    perfiles["prob_positivo_media"] = perfiles["prob_positivo_media"].round(4)

    columnas_finales = [
        "book_id",
        "book_title",
        "Negativo",
        "Neutral",
        "Positivo",
        "total_reviews",
        "ratio_negativo",
        "ratio_neutral",
        "ratio_positivo",
        "sentimiento_dominante",
        "score_medio",
        "prob_negativo_media",
        "prob_neutral_media",
        "prob_positivo_media",
    ]

    for columna in reversed(columnas_extra):
        columnas_finales.insert(2, columna)

    perfiles = perfiles[columnas_finales].copy()

    perfiles = perfiles.sort_values(
        by=["total_reviews", "score_medio"],
        ascending=[False, False],
    )

    print("Perfiles creados:", len(perfiles))

    print("\nDistribución de sentimiento dominante:")
    print(perfiles["sentimiento_dominante"].value_counts())

    return perfiles


def guardar_perfiles(perfiles):
    print("\n=== GUARDANDO PERFILES ===")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    perfiles.to_csv(OUTPUT_PATH, index=False)

    print("Archivo creado:", OUTPUT_PATH)
    print("Total perfiles:", len(perfiles))

    print("\nPrimeros perfiles:")
    print(perfiles.head(10))


def main():
    df = cargar_dataset()
    df = validar_dataset(df)

    predictor = PredictorSentimientos(batch_size=BATCH_SIZE)

    df = predecir_sentimientos_con_cache(df, predictor)
    perfiles = crear_perfiles_emocionales(df)
    guardar_perfiles(perfiles)

    print("\n--- PERFILES EMOCIONALES GENERADOS CORRECTAMENTE ---")


if __name__ == "__main__":
    main()
