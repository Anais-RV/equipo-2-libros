import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

print("1. Cargando el dataset original de GoodReads...")
df = pd.read_csv("Books_Dataset_GoodReads.csv")

print("2. Aplicando limpieza inicial contra nulos...")
df_limpio = df.dropna(subset=["book_title", "author", "book_details", "genres", "review_rating"]).copy()
df_limpio = df_limpio.drop_duplicates()
df_limpio["book_details"] = df_limpio["book_details"].astype(str)

print("3. Extrayendo los géneros principales de forma segura...")

def limpiar_genero_seguro(texto_genero):
    texto_limpio = str(texto_genero).strip("[]")
    partes = texto_limpio.split(",")
    if len(partes) > 0:
        return partes[0].strip().strip("'").strip('"')
    return None

df_limpio["main_genre"] = df_limpio["genres"].apply(limpiar_genero_seguro)
df_limpio = df_limpio.dropna(subset=["main_genre"])

print("4. Unificando sentimientos...")

def clasificar_sentimiento(rating):
    if rating in [4, 5]:
        return "Positivo"
    elif rating == 3:
        return "Neutral"
    elif rating in [1, 2]:
        return "Negativo"
    return None

df_limpio["sentimiento_etiqueta"] = df_limpio["review_rating"].apply(clasificar_sentimiento)
df_limpio = df_limpio.dropna(subset=["sentimiento_etiqueta"])

top_genres = df_limpio["main_genre"].value_counts().head(5).index
df_top = df_limpio[df_limpio["main_genre"].isin(top_genres)].copy()

print("5. Eliminando libros repetidos...")

df_top = (
    df_top
    .groupby("book_title", as_index=False)
    .agg({
        "author": "first",
        "book_details": "first",
        "review_rating": "mean",
        "sentimiento_etiqueta": lambda x: x.mode()[0],
        "main_genre": lambda x: x.mode()[0]
    })
)

df_top["review_rating"] = df_top["review_rating"].round(1)

print(f"-> Dataset final listo con {len(df_top)} libros únicos.")

print("\n6. Configurando variables y dividiendo el dataset...")
X = df_top[["book_details", "review_rating"]]
y = df_top["main_genre"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\n7. Entrenando el modelo híbrido...")
preprocesador = ColumnTransformer(
    transformers=[
        ("texto_nlp", TfidfVectorizer(stop_words="english", max_features=5000), "book_details"),
        ("sentimiento_num", StandardScaler(), ["review_rating"])
    ]
)

pipeline_modelo = Pipeline(steps=[
    ("preprocesador", preprocesador),
    ("clasificador", LogisticRegression(max_iter=2000))
])

pipeline_modelo.fit(X_train, y_train)

y_pred = pipeline_modelo.predict(X_test)
print(f"-> Modelo entrenado. Precisión: {accuracy_score(y_test, y_pred) * 100:.2f}%")

print("\n8. Guardando archivos...")
joblib.dump(pipeline_modelo, "modelo_hibrido_libros.pkl")

columnas_finales = [
    "book_title",
    "author",
    "book_details",
    "review_rating",
    "sentimiento_etiqueta",
    "main_genre"
]

df_top[columnas_finales].to_csv("dataset_para_analisis_sentimientos.csv", index=False)

print("Guardado:")
print("- modelo_hibrido_libros.pkl")
print("- dataset_para_analisis_sentimientos.csv")

print("\n9. Prueba rápida...")

def probar_modelo_local(sinopsis_libro, rating_review):
    nuevo_libro = pd.DataFrame({
        "book_details": [sinopsis_libro],
        "review_rating": [rating_review]
    })

    genero_predicho = pipeline_modelo.predict(nuevo_libro)[0]

    print("--- Prueba en Vivo ---")
    print(f"Texto: '{sinopsis_libro[:60]}...'")
    print(f"Rating: {rating_review}")
    print(f"Género asociado: {genero_predicho}\n")

probar_modelo_local(
    "A terrifying haunting in an abandoned asylum where ghosts scare investigators.",
    2
)

probar_modelo_local(
    "A beautiful romantic story about two lovers meeting in Paris during the spring.",
    5
)

print("--- PROCESO FINALIZADO ---")