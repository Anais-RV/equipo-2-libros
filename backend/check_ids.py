import csv

CSV_FILE = 'Books_Dataset_GoodReads.csv'

def list_unique_books():
    unique_ids = set()
    print("--- ESCANEANDO ARCHIVO (MODO SEGURO) ---")
    
    try:
        # Abrimos el archivo de forma manual para evitar el Buffer Overflow de Pandas
        with open(CSV_FILE, mode='r', encoding='latin-1', errors='ignore') as f:
            # Usamos un lector básico que no se bloquea por el tamaño de línea
            reader = csv.DictReader(f)
            
            # Limpiamos los nombres de las columnas manualmente
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            
            count = 0
            for row in reader:
                bid = row.get('book_id')
                if bid:
                    unique_ids.add(bid)
                
                # Para no esperar horas, paramos al encontrar los primeros IDs distintos
                if len(unique_ids) >= 20:
                    break
        
        print(f"\n✅ IDs encontrados para probar:")
        print("-" * 30)
        for bid in sorted(list(unique_ids)):
            print(f"ID del libro: {bid}")
        print("-" * 30)
        print("Elige uno de estos números para tu análisis.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    list_unique_books()