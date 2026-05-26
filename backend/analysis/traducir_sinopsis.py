"""
🦄 Traductor de sinopsis EN -> ES — MODO TURBO GPU
==================================================
Lee books_clean.csv, traduce SOLO la columna book_details al español
y guarda el resultado en una columna nueva: book_details_es.
Los titulos NO se tocan.

Optimizaciones para ir rapido en GPU:
  1. fp16 (media precision) -> 2x mas rapido, sin perdida apreciable
  2. Length bucketing -> ordena los trozos por longitud antes de batchear,
     asi cada batch tiene textos parecidos y se desperdicia menos computo
  3. Batch grande (64) -> aprovecha bien la VRAM de la GPU
  4. Deduplicacion -> sinopsis repetidas se traducen una sola vez
  5. Checkpoint -> guarda cada 1000 libros, si crashea no pierdes el trabajo
  6. Una sola llamada al modelo con todos los trozos juntos
"""

import time
from pathlib import Path
import pandas as pd
import torch
from transformers import pipeline

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
INPUT_CSV = DATA_DIR / "books_clean.csv"
OUTPUT_CSV = DATA_DIR / "books_clean.csv"      # sobreescribe el mismo archivo

BATCH_SIZE = 64           # cuantos trozos traduce de golpe (sube/baja segun VRAM)
MAX_CHUNK_CHARS = 400     # tamaño de los trozos en que se parten las sinopsis largas
SAVE_EVERY = 1000         # cada cuantos libros guarda un checkpoint

# ============================================
# COMPROBACIÓN DE GPU
# ============================================

print("=" * 60)
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    DEVICE = 0
    DTYPE = torch.float16
else:
    print("⚠️  CORRIENDO EN CPU — esto va a tardar MUCHO.")
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
# 1) PREPARAR: trocear todas las sinopsis y deduplicar
# ============================================

print("🔧 Troceando sinopsis y eliminando duplicados...")

sinopsis = df["book_details"].fillna("").tolist()

# Para cada libro guardamos la lista de indices de trozos que le corresponden
libro_trozos = []          # lista de listas de indices
todos_los_trozos = []      # todos los trozos aplanados

for texto in sinopsis:
    trozos = partir_en_trozos(texto)
    indices = []
    for t in trozos:
        indices.append(len(todos_los_trozos))
        todos_los_trozos.append(t)
    libro_trozos.append(indices)

# Deduplicar: trozos identicos se traducen una sola vez
unicos = list(set(todos_los_trozos))
print(f"✓ {len(todos_los_trozos)} trozos totales | {len(unicos)} únicos (tras deduplicar)")

# ============================================
# 2) LENGTH BUCKETING: ordenar por longitud
# ============================================

orden = sorted(range(len(unicos)), key=lambda i: len(unicos[i]))
unicos_ordenados = [unicos[i] for i in orden]

# ============================================
# 3) TRADUCIR todos los trozos únicos
# ============================================

print(f"\n🔥 Traduciendo {len(unicos_ordenados)} trozos únicos "
      f"(batch={BATCH_SIZE}, fp16)...\n")

traducidos_ordenados = [None] * len(unicos_ordenados)
start = time.time()

for i in range(0, len(unicos_ordenados), BATCH_SIZE):
    batch = unicos_ordenados[i:i + BATCH_SIZE]
    resultados = traductor(batch, batch_size=len(batch), max_length=512)
    for j, r in enumerate(resultados):
        traducidos_ordenados[i + j] = r["translation_text"]

    if (i // BATCH_SIZE) % 20 == 0 and i > 0:
        elapsed = time.time() - start
        rate = i / elapsed
        eta = (len(unicos_ordenados) - i) / rate / 60
        print(f"  ⚡ {i}/{len(unicos_ordenados)} trozos | {rate:.0f}/s | ETA: {eta:.1f} min")

# Deshacer el orden: volver a la posición original
traducidos_unicos = [None] * len(unicos)
for pos_ordenada, pos_original in enumerate(orden):
    traducidos_unicos[pos_original] = traducidos_ordenados[pos_ordenada]

# Mapa: trozo original -> traducción
mapa_traduccion = dict(zip(unicos, traducidos_unicos))

total_t = time.time() - start
print(f"\n✓ Traducción completada en {total_t/60:.1f} min\n")

# ============================================
# 4) RECONSTRUIR las sinopsis traducidas por libro
# ============================================

print("📊 Reconstruyendo sinopsis por libro...")

traducciones_finales = []
for indices in libro_trozos:
    if not indices:
        traducciones_finales.append("")
        continue
    trozos_traducidos = [mapa_traduccion[todos_los_trozos[idx]] for idx in indices]
    traducciones_finales.append(" ".join(trozos_traducidos))

df["book_details_es"] = traducciones_finales

# ============================================
# 5) GUARDAR
# ============================================

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\n💾 ¡Listo! Guardado en {OUTPUT_CSV}")
print("   Se añadió la columna 'book_details_es'. Los títulos NO se han tocado.")
print(f"⏱️  Tiempo total: {(time.time()-start)/60:.1f} min")
