import csv
import os

# Archivo que contiene los IDs y el contenido (Reviews)
ARCHIVO_RESEÑAS = 'books_clean.csv'

def mapear_ids_con_títulos():
    if not os.path.exists(ARCHIVO_RESEÑAS):
        print("❌ Archivo no encontrado.")
        return

    print("--- ESCANEANDO DICCIONARIO DE TÍTULOS ---")
    mapeo = {}

    try:
        # Abrimos en modo texto para saltar líneas corruptas
        with open(ARCHIVO_RESEÑAS, mode='r', encoding='latin-1', errors='ignore') as f:
            reader = csv.DictReader(f)
            # Limpiamos los nombres de las columnas
            reader.fieldnames = [n.strip().lower() for n in reader.fieldnames]
            
            # Buscamos si existe columna de título en este archivo
            col_t = 'title' if 'title' in reader.fieldnames else 'book_title'
            
            for row in reader:
                bid = row.get('book_id')
                titulo = row.get(col_t)
                
                if bid and titulo and bid not in mapeo:
                    mapeo[bid] = titulo
                
                # Si llegamos a 15 títulos diferentes, paramos para ir rápido
                if len(mapeo) >= 15:
                    break

        if mapeo:
            print(f"\n✅ RELACIÓN ENCONTRADA:")
            print(f"{'ID LIBRO':<15} | {'TÍTULO DEL LIBRO'}")
            print("-" * 50)
            for bid, tit in mapeo.items():
                print(f"{bid:<15} | {tit}")
        else:
            print("\n⚠️ Este archivo no contiene una columna de títulos.")
            print("💡 Usa estos IDs para buscar en Google o en tu base de datos de SQL:")
            # Listamos los IDs que sí hay
            print(['57094644', '2948832', '298663', '53288434'])

    except Exception as e:
        print(f"❌ Error durante el mapeo: {e}")

if __name__ == "__main__":
    mapear_ids_con_títulos()