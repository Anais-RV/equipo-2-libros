from pathlib import Path
import re
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
DATA_DIR = ROOT_DIR / "data"

BOOKS_CSV = DATA_DIR / "books_clean.csv"
REVIEWS_CSV = DATA_DIR / "reviews_clean.csv"
OUTPUT_CSV = DATA_DIR / "dataset_bert_sentimientos.csv"

# Configuración
FILTRAR_SOLO_INGLES = False
MIN_REVIEW_WORDS = 3


def extraer_rating(valor):
    """
    Convierte valores como:
    - 'Rating 5 out of 5'
    - '5'
    - 5
    en un número entero del 1 al 5.
    """
    if pd.isna(valor):
        return None

    texto = str(valor)
    match = re.search(r"([1-5])", texto)

    if match:
        return int(match.group(1))

    return None


def clasificar_sentimiento(rating):
    """
    Unifica ratings:
    1 y 2 -> Negativo
    3 -> Neutral
    4 y 5 -> Positivo
    """
    if rating in [1, 2]:
        return "Negativo"

    if rating == 3:
        return "Neutral"

    if rating in [4, 5]:
        return "Positivo"

    return None


def limpiar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)
    texto = texto.replace("\n", " ").replace("\r", " ")
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()

    return texto


def contar_exclamaciones(texto):
    return str(texto).count("!") if not pd.isna(texto) else 0


def contar_interrogaciones(texto):
    return str(texto).count("?") if not pd.isna(texto) else 0


def calcular_ratio_mayusculas(texto):
    if pd.isna(texto):
        return 0.0

    letras = [c for c in str(texto) if c.isalpha()]

    if not letras:
        return 0.0

    mayusculas = [c for c in letras if c.isupper()]
    return len(mayusculas) / len(letras)


def normalizar_columna_language(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    equivalencias_ingles = {
        "english",
        "eng",
        "en",
        "en-us",
        "en-gb",
        "us english",
        "uk english",
    }

    if texto in equivalencias_ingles:
        return "english"

    return texto


def validar_archivos():
    if not BOOKS_CSV.exists():
        raise FileNotFoundError(f"No existe books_clean.csv en: {BOOKS_CSV}")

    if not REVIEWS_CSV.exists():
        raise FileNotFoundError(f"No existe reviews_clean.csv en: {REVIEWS_CSV}")


def cargar_datos():
    print("=== CARGANDO CSV BASE ===")
    print("Books:", BOOKS_CSV)
    print("Reviews:", REVIEWS_CSV)

    books = pd.read_csv(BOOKS_CSV)
    reviews = pd.read_csv(REVIEWS_CSV)

    print("Books cargados:", len(books))
    print("Reviews cargadas:", len(reviews))

    return books, reviews


def preparar_reviews(reviews):
    print("\n=== PREPARANDO REVIEWS ===")

    columnas_necesarias = ["book_id", "review_rating", "clean_review"]

    for columna in columnas_necesarias:
        if columna not in reviews.columns:
            raise ValueError(f"Falta la columna obligatoria en reviews: {columna}")

    reviews = reviews.dropna(subset=["book_id", "review_rating", "clean_review"]).copy()

    reviews["book_id"] = reviews["book_id"].astype(str).str.strip()
    reviews["clean_review"] = reviews["clean_review"].apply(limpiar_texto)

    reviews = reviews[reviews["book_id"] != ""]
    reviews = reviews[reviews["clean_review"] != ""]

    reviews["review_word_count"] = reviews["clean_review"].str.split().str.len()
    reviews = reviews[reviews["review_word_count"] >= MIN_REVIEW_WORDS].copy()

    reviews["rating_num"] = reviews["review_rating"].apply(extraer_rating)
    reviews = reviews.dropna(subset=["rating_num"]).copy()
    reviews["rating_num"] = reviews["rating_num"].astype(int)

    reviews["sentimiento_etiqueta"] = reviews["rating_num"].apply(clasificar_sentimiento)
    reviews = reviews.dropna(subset=["sentimiento_etiqueta"]).copy()

    reviews["is_negative_rating"] = reviews["rating_num"].isin([1, 2]).astype(int)
    reviews["is_neutral_rating"] = (reviews["rating_num"] == 3).astype(int)
    reviews["is_positive_rating"] = reviews["rating_num"].isin([4, 5]).astype(int)

    reviews["review_length"] = reviews["clean_review"].str.len()
    reviews["review_exclamation_count"] = reviews["clean_review"].apply(contar_exclamaciones)
    reviews["review_question_count"] = reviews["clean_review"].apply(contar_interrogaciones)
    reviews["review_uppercase_ratio"] = reviews["clean_review"].apply(calcular_ratio_mayusculas)

    # Duplicado real: mismo libro + misma review + mismo rating.
    reviews = reviews.drop_duplicates(subset=["book_id", "clean_review", "rating_num"])

    print("Reviews válidas:", len(reviews))
    print("\nDistribución por rating:")
    print(reviews["rating_num"].value_counts().sort_index())
    print("\nDistribución por sentimiento derivado del rating:")
    print(reviews["sentimiento_etiqueta"].value_counts())

    return reviews


def preparar_books(books):
    print("\n=== PREPARANDO BOOKS ===")

    if "book_id" not in books.columns:
        raise ValueError("Falta la columna obligatoria en books: book_id")

    books = books.dropna(subset=["book_id"]).copy()
    books["book_id"] = books["book_id"].astype(str).str.strip()
    books = books[books["book_id"] != ""]

    columnas_deseadas = [
        "book_id",
        "book_title",
        "author",
        "genres",
        "book_details",
        "average_rating",
        "language",
    ]

    columnas_existentes = [col for col in columnas_deseadas if col in books.columns]
    books = books[columnas_existentes].copy()

    for columna in ["book_title", "author", "genres", "book_details", "language"]:
        if columna in books.columns:
            books[columna] = books[columna].apply(limpiar_texto)

    if "language" in books.columns:
        books["language_normalized"] = books["language"].apply(normalizar_columna_language)

        if FILTRAR_SOLO_INGLES:
            antes = len(books)
            books = books[books["language_normalized"] == "english"].copy()
            print(f"Filtro inglés activo: {antes} -> {len(books)} libros")

    books = books.drop_duplicates(subset=["book_id"])

    print("Books válidos:", len(books))

    return books


def crear_dataset_final(books, reviews):
    print("\n=== UNIENDO BOOKS + REVIEWS ===")

    df = reviews.merge(books, on="book_id", how="inner")

    print("Registros después del merge:", len(df))

    if df.empty:
        raise ValueError("El dataset quedó vacío después del merge. Revisa book_id en ambos CSV.")

    print("\n=== CREANDO TEXTO PARA MODELO PREENTRENADO ===")

    # Importante:
    # Para sentimiento usamos SOLO la review.
    # La descripción se conserva como metadato, pero no se mezcla con la review.
    df["texto_bert"] = df["clean_review"].astype(str).apply(limpiar_texto)

    df = df[df["texto_bert"] != ""].copy()

    columnas_finales = [
        "book_id",
        "book_title",
        "author",
        "genres",
        "book_details",
        "clean_review",
        "texto_bert",
        "review_rating",
        "rating_num",
        "sentimiento_etiqueta",
        "is_negative_rating",
        "is_neutral_rating",
        "is_positive_rating",
        "review_length",
        "review_word_count",
        "review_exclamation_count",
        "review_question_count",
        "review_uppercase_ratio",
        "average_rating",
        "language",
        "language_normalized",
    ]

    columnas_finales = [col for col in columnas_finales if col in df.columns]
    df_final = df[columnas_finales].copy()

    df_final = df_final.drop_duplicates(subset=["book_id", "texto_bert", "rating_num"])

    return df_final


def guardar_dataset(df_final):
    print("\n=== GUARDANDO DATASET FINAL ===")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(OUTPUT_CSV, index=False)

    print("Dataset creado:", OUTPUT_CSV)
    print("Total registros:", len(df_final))
    print("Libros únicos:", df_final["book_id"].nunique())

    print("\nDistribución final de sentimientos:")
    print(df_final["sentimiento_etiqueta"].value_counts())

    print("\nColumnas generadas:")
    print(df_final.columns.tolist())


def main():
    validar_archivos()
    books, reviews = cargar_datos()
    reviews = preparar_reviews(reviews)
    books = preparar_books(books)
    df_final = crear_dataset_final(books, reviews)
    guardar_dataset(df_final)

    print("\n--- DATASET DE SENTIMIENTOS PREPARADO CORRECTAMENTE ---")


if __name__ == "__main__":
    main()
