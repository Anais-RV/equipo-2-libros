import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

print("1. Cargando el dataset optimizado para sentimientos...")
# Este script lee el CSV limpio que generó tu primer programa
df = pd.read_csv('dataset_para_analisis_sentimientos.csv')

# Filtro de seguridad rápido
df = df.dropna(subset=['book_details', 'sentimiento_etiqueta']).copy()
df['book_details'] = df['book_details'].astype(str)

print(f"-> Dataset cargado. Total de registros: {len(df)}")

print("\n2. Preparando variables y dividiendo datos...")
X = df['book_details']
y = df['sentimiento_etiqueta']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("\n3. Convirtiendo texto a variables matemáticas (TF-IDF)...")
vectorizador_sentimientos = TfidfVectorizer(stop_words='english', max_features=5000)
X_train_tfidf = vectorizador_sentimientos.fit_transform(X_train)
X_test_tfidf = vectorizador_sentimientos.transform(X_test)

print("\n4. Entrenando el clasificador de sentimientos...")
modelo_sentimientos = LogisticRegression(max_iter=1000)
modelo_sentimientos.fit(X_train_tfidf, y_train)

y_pred = modelo_sentimientos.predict(X_test_tfidf)
print(f"-> ¡Modelo entrenado! Precisión: {accuracy_score(y_test, y_pred) * 100:.2f}%")

print("\n5. GUARDANDO ARCHIVOS FÍSICOS EN TU DISCO...")
# ¡AQUÍ ES DONDE SE CREAN LOS ARCHIVOS QUE TE FALTAN!
joblib.dump(modelo_sentimientos, 'clasificador_sentimientos.pkl')
joblib.dump(vectorizador_sentimientos, 'vectorizador_sentimientos.pkl')
print("¡ÉXITO! Guardado como: 'clasificador_sentimientos.pkl' y 'vectorizador_sentimientos.pkl'")

print("\n6. EJECUTANDO PRUEBA RÁPIDA...")
def probar_sentimiento(texto):
    transformado = vectorizador_sentimientos.transform([texto])
    prediccion = modelo_sentimientos.predict(transformado)[0]
    print(f"Texto: '{texto[:50]}...' => Sentimiento: {prediccion}")

probar_sentimiento("This book was amazing, wonderful and beautifully written!")
probar_sentimiento("I hated this story. It was so boring and a complete waste of time.")

print("\n--- ¡PROCESO FINALIZADO CON ÉXITO! ---")