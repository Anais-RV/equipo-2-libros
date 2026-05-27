import pandas as pd
import os
from trainer_bert import get_sentiment_profile

CSV_FILE = 'Books_Dataset_GoodReads.csv'

# Mapeo de nombres para la presentación
LIBROS_NOMBRES = {
    "1": "Harry Potter and the Sorcerer's Stone",
    "53288434": "The Midnight Library",
    "57094644": "The Maid"
}

def load_data():
    if not os.path.exists(CSV_FILE):
        print("❌ Archivo CSV no encontrado.")
        return None
    # Carga robusta Latin-1
    df = pd.read_csv(CSV_FILE, encoding='latin-1', sep=None, engine='python', on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower()
    return df

def analyze_logic(dataframe, limit=10):
    col_texto = 'review_content' if 'review_content' in dataframe.columns else 'book_details'
    results = []
    for text in dataframe[col_texto].head(limit):
        results.append(get_sentiment_profile(text))
    return pd.DataFrame(results)

def print_results(df_results, title):
    avg = df_results.mean().round(4).to_dict()
    print("\n" + "═"*50)
    print(f" ANÁLISIS: {title.upper()} ")
    print("═"*50)
    for emo, val in avg.items():
        barra = "█" * int(val * 25)
        print(f" {emo.capitalize():<18} | {val:>6} {barra}")
    print("═"*50)

if __name__ == "__main__":
    df_full = load_data()
    
    if df_full is not None:
        # OPCIÓN A: Analizar un libro específico (ejemplo ID 1)
        id_test = "1"
        df_book = df_full[df_full['book_id'].astype(str) == id_test]
        res_book = analyze_logic(df_book)
        print_results(res_book, LIBROS_NOMBRES.get(id_test, id_test))

        # OPCIÓN B: Analizar TODO el dataset (Muestra de 100 líneas)
        print("\n[INFO] Realizando análisis global de todo el dataset...")
        res_global = analyze_logic(df_full, limit=100)
        print_results(res_global, "Sentimiento General del Dataset")