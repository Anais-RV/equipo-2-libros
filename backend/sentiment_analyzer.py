import pandas as pd
import os
from trainer_bert import get_sentiment_profile

CSV_FILE = 'Books_Dataset_GoodReads.csv'

# Metadatos para que la terminal se vea profesional
LIBROS_NOMBRES = {
    "1": "Harry Potter and the Sorcerer's Stone",
    "57094644": "The Maid",
    "53288434": "The Midnight Library",
    "2948832": "The Help"
}

def load_book_reviews(id_buscado: str) -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    # Carga robusta (Latin-1) para evitar errores de codificación
    df = pd.read_csv(CSV_FILE, encoding='latin-1', sep=None, engine='python', on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower()
    return df[df['book_id'].astype(str) == str(id_buscado)]

def analyze_sentiment(id_buscado: str):
    df_book = load_book_reviews(id_buscado)
    if df_book.empty:
        return None

    col_texto = 'review_content' if 'review_content' in df_book.columns else 'book_details'
    
    # Procesamos los sentimientos de cada reseña encontrada (limitamos a 10 para la vista)
    perfiles_detectados = []
    print(f"-> Analizando {len(df_book.head(10))} reseñas individuales...")
    
    for i, texto in enumerate(df_book[col_texto].head(10)):
        perfil = get_sentiment_profile(texto)
        perfil['Reseña_Nº'] = i + 1
        perfiles_detectados.append(perfil)
    
    return pd.DataFrame(perfiles_detectados)

if __name__ == "__main__":
    # ID de prueba (puedes cambiarlo al que quieras)
    ID_TEST = "1" 
    nombre_libro = LIBROS_NOMBRES.get(ID_TEST, f"ID: {ID_TEST}")
    
    print(f"\n[SISTEMA] Iniciando análisis detallado de: {nombre_libro}")
    df_resultados = analyze_sentiment(ID_TEST)
    
    if df_resultados is not None:
        # 1. MOSTRAR TABLA DE PERFILES INDIVIDUALES
        print("\n" + "═"*80)
        print(f" DETALLE DE PERFILES ENCONTRADOS (MUESTRA POR RESEÑA) ")
        print("═"*80)
        # Seleccionamos las columnas principales para que quepan en la terminal
        cols = ['Reseña_Nº', 'joy', 'sadness', 'fear', 'surprise', 'anger']
        print(df_resultados[cols].to_string(index=False))
        
        # 2. MOSTRAR PROMEDIO FINAL CON BARRAS VISUALES
        promedio = df_resultados.drop(columns=['Reseña_Nº']).mean().round(4)
        
        print("\n" + "═"*80)
        print(f" RESUMEN EMOCIONAL GLOBAL: {nombre_libro.upper()} ")
        print("═"*80)
        for emocion, valor in promedio.to_dict().items():
            # Creamos una barra visual para la defensa del proyecto
            barra = "█" * int(valor * 30)
            print(f" {emocion.capitalize():<18} | {valor:>6} {barra}")
        print("═"*80)