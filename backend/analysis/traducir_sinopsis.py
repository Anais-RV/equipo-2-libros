"""
🦄 Traductor de sinopsis EN -> ES — MODO TURBO GPU + CHECKPOINTS
================================================================
Lee books_clean.csv, traduce SOLO la columna book_details al español
y guarda el resultado en una columna nueva: book_details_es.
Los titulos NO se tocan.

Optimizaciones:
  1. fp16 (media precision) -> 2x mas rapido
  2. Length bucketing -> ordena por longitud, padding minimo
  3. Deduplicacion -> trozos repetidos se traducen una sola vez
  4. CHECKPOINTS -> guarda el progreso cada N trozos. Si crashea,
     al reiniciar retoma desde donde iba (no empieza de cero)
  5. truncation=True -> trozos demasiado largos se recortan en vez de petar
"""

import time
import json
from pathlib import Path
import pandas as pd
import torch
from transformers import pipeline

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
INPUT_CSV = DATA_DIR / "books_clean.csv"
OUTPUT_CSV = DATA_DIR / "books_clean.csv"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "cache"
CHECKPOINT_FILE = CACHE_DIR / "traduccion_checkpoint.json"

BATCH_SIZE = 32
MAX_CHUNK_CHARS = 200      # tamaño de los trozos (caracteres)
SAVE_EVERY = 500           # guarda checkpoint cada N trozos traducidos

# ============================================
# COMPROBACIÓN DE GPU
# ============================================

print("=" * 60)
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    DEVICE = 0
    DTYPE = torch.float16
else:
    print("⚠️  CORRIENDO EN CPU — va a tardar mucho.")
    DEVICE = -1
    DTYPE = torch.float32
print("=" * 60 + "\n")

# ============================================
# CARGAR MODELO
# ============================================

print("🦄 Cargando modelo Helsinki-NLP/opus-mt-en-es (fp16)...")
traductor = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-en-es",
    device=DEVICE,
    torch_dtype=DTYPE,
)

# ============================================
# CARGAR CSV
# ============================================

print("📚 Cargando books_clean.csv...")
df = pd.read_csv(INPUT_CSV, on_bad_lines="skip", engine="python")

if "book_details" not in df.columns:
    raise ValueError("No se encontró la columna 'book_details' en el CSV")

print(f"✓ {len(df)} libros cargados\n")

# ============================================
# HELPERS
# ============================================

def partir_en_trozos(texto, max_chars=MAX_CHUNK_CHARS):
    """Parte un texto largo en trozos respetando los puntos."""
    texto = str(texto).strip()
    if not texto:
        return []
    if len(texto) <= max_chars:
        return [texto]

    trozos = []
    actual = ""
    for frase in texto.split(". "):
        if len(actual) + len(frase) < max_chars:
            actual += frase + ". "
        else:
            if actual:
                trozos.append(actual.strip())
            actual = frase + ". "
    if actual:
        trozos.append(actual.strip())
    return trozos


# ============================================
# 1) PREPARAR: trocear y deduplicar
# ============================================

print("🔧 Troceando sinopsis y eliminando duplicados...")

sinopsis = df["book_details"].fillna("").tolist()

libro_trozos = []
todos_los_trozos = []

for texto in sinopsis:
    trozos = partir_en_trozos(texto)
    indices = []
    for t in trozos:
        indices.append(len(todos_los_trozos))
        todos_los_trozos.append(t)
    libro_trozos.append(indices)

unicos = list(set(todos_los_trozos))
print(f"✓ {len(todos_los_trozos)} trozos totales | {len(unicos)} únicos\n")

# ============================================
# 2) CHECKPOINT: cargar progreso previo si existe
# ============================================

# El checkpoint guarda un diccionario {trozo_original: traduccion}
traducciones_guardadas = {}
if CHECKPOINT_FILE.exists():
    try:
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            traducciones_guardadas = json.load(f)
        print(f"♻️  Checkpoint encontrado: {len(traducciones_guardadas)} trozos ya traducidos\n")
    except Exception:
        traducciones_guardadas = {}

# Solo traducimos los trozos que NO estén ya en el checkpoint
pendientes = [t for t in unicos if t not in traducciones_guardadas]
print(f"📊 {len(pendientes)} trozos pendientes de traducir\n")

# ============================================
# 3) LENGTH BUCKETING + TRADUCIR
# ============================================

if pendientes:
    orden = sorted(range(len(pendientes)), key=lambda i: len(pendientes[i]))
    pendientes_ordenados = [pendientes[i] for i in orden]

    print(f"🔥 Traduciendo (batch={BATCH_SIZE}, fp16)...\n")
    start = time.time()

    for i in range(0, len(pendientes_ordenados), BATCH_SIZE):
        batch = pendientes_ordenados[i:i + BATCH_SIZE]
        try:
            resultados = traductor(batch, batch_size=len(batch),
                                   max_length=512, truncation=True)
            for original, r in zip(batch, resultados):
                traducciones_guardadas[original] = r["translation_text"]
        except Exception as e:
            print(f"  ✗ Error en batch {i}: {e}")
            # si falla un batch, deja los originales
            for original in batch:
                traducciones_guardadas[original] = original

        # CHECKPOINT: guardar progreso
        if (i // BATCH_SIZE) % (SAVE_EVERY // BATCH_SIZE) == 0 and i > 0:
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(traducciones_guardadas, f, ensure_ascii=False)
            elapsed = time.time() - start
            rate = i / elapsed
            eta = (len(pendientes_ordenados) - i) / rate / 60
            print(f"  💾 Checkpoint: {i}/{len(pendientes_ordenados)} | "
                  f"{rate:.0f}/s | ETA: {eta:.1f} min")

    # Guardar checkpoint final
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(traducciones_guardadas, f, ensure_ascii=False)
    print(f"\n✓ Traducción completada en {(time.time()-start)/60:.1f} min\n")
else:
    print("✓ Todo estaba ya traducido en el checkpoint.\n")

# ============================================
# 4) RECONSTRUIR las sinopsis por libro
# ============================================

print("📊 Reconstruyendo sinopsis por libro...")

traducciones_finales = []
for indices in libro_trozos:
    if not indices:
        traducciones_finales.append("")
        continue
    trozos_traducidos = [
        traducciones_guardadas.get(todos_los_trozos[idx], todos_los_trozos[idx])
        for idx in indices
    ]
    traducciones_finales.append(" ".join(trozos_traducidos))

df["book_details_es"] = traducciones_finales

# ============================================
# 5) GUARDAR CSV FINAL
# ============================================

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\n💾 ¡Listo! Guardado en {OUTPUT_CSV}")
print("   Se añadió la columna 'book_details_es'. Los títulos no se han tocado.")

# Borrar el checkpoint, ya no hace falta
if CHECKPOINT_FILE.exists():
    CHECKPOINT_FILE.unlink()
    print("🧹 Checkpoint temporal eliminado.")