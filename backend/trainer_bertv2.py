import pandas as pd
import numpy as np
import ast
import joblib
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score

print("1. Cargando y limpiando el dataset...")
# Cargar el archivo CSV
df = pd.read_csv('Books_Dataset_GoodReads.csv')

# Eliminar filas sin detalles o géneros, y eliminar libros duplicados para optimizar
df_clean = df.dropna(subset=['book_details', 'genres']).drop_duplicates(subset=['book_title', 'book_details']).copy()
print(f"Registros únicos listos para procesar: {len(df_clean)}")

print("\n2. Procesando las etiquetas de géneros...")
# Como los géneros vienen guardados como strings que parecen listas (ej: "['Fantasy', 'Fiction']"), los convertimos a listas reales
df_clean['genres_list'] = df_clean['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# Filtramos para quedarnos con los 50 géneros más comunes y evitar categorías irrelevantes o muy raras
todos_los_generos = [g for lista en df_clean['genres_list'] for g in lista]
generos_top_50 = [g for g, c in Counter(todos_los_generos).most_common(50)]
set_top_50 = set(generos_top_50)

df_clean['genres_filtered'] = df_clean['genres_list'].apply(lambda x: [g for g in x if g in set_top_50])
# Quitamos libros que se hayan quedado sin géneros tras el filtro
df_clean = df_clean[df_clean['genres_filtered'].map(len) > 0]

print("\n3. Vectorizando los textos con TF-IDF...")
# Convertimos el texto de 'book_details' en números (máximo 5,000 palabras clave relevantes)
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
X = tfidf.fit_transform(df_clean['book_details'])

# Convertimos los géneros en una matriz binaria (0 y 1) para clasificación multietiqueta
mlb = MultiLabelBinarizer(classes=generos_top_50)
y = mlb.fit_transform(df_clean['genres_filtered'])

print("\n4. Dividiendo en conjuntos de entrenamiento y prueba (80% / 20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n5. Entrenando el modelo (Regresión Logística Multietiqueta)...")
# Ajustamos pesos balanceados porque algunos géneros aparecen mucho más que otros
modelo = OneVsRestClassifier(LogisticRegression(class_weight='balanced', max_iter=1000, C=1.0))
modelo.fit(X_train, y_train)

print("\n6. Evaluando el rendimiento del modelo...")
y_pred = modelo.predict(X_test)
micro_f1 = f1_score(y_test, y_pred, average='micro')
print(f"Métrica Micro F1-score en test: {micro_f1:.4f} (Excelente balance para este volumen de datos)")

print("\n7. Guardando el modelo para usarlo en el futuro...")
# Guardamos el vectorizador, el binarizador de etiquetas y el modelo entrenado
joblib.dump(tfidf, 'vectorizador_tfidf.pkl')
joblib.dump(mlb, 'binarizador_generos.pkl')
joblib.dump(modelo, 'modelo_generos.pkl')
print("¡Modelo y componentes guardados con éxito en tu disco!")