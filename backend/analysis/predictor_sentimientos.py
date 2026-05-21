from pathlib import Path
import math
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
MAX_LENGTH = 512
DEFAULT_BATCH_SIZE = 32


class PredictorSentimientos:
    """
    Predictor de sentimientos con modelo preentrenado de Hugging Face.

    Devuelve:
    - sentimiento: Negativo / Neutral / Positivo
    - sentimiento_modelo: etiqueta original del modelo
    - score: probabilidad de la clase elegida
    - probabilidades: probabilidad por clase normalizada a español
    """

    def __init__(
        self,
        model_name=MODEL_NAME,
        batch_size=DEFAULT_BATCH_SIZE,
        max_length=MAX_LENGTH,
        aplicar_reglas_neutral=True,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        self.aplicar_reglas_neutral = aplicar_reglas_neutral

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print("=== CARGANDO MODELO PREENTRENADO DE SENTIMIENTOS ===")
        print("Modelo:", self.model_name)
        print("Device:", self.device)

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label

        print("Etiquetas del modelo:", self.id2label)
        print("Modelo cargado correctamente.")

    def preparar_texto(self, texto):
        if texto is None:
            return ""

        texto = str(texto)
        texto = texto.replace("\n", " ").replace("\r", " ")
        texto = " ".join(texto.split())
        texto = texto.strip()

        return texto

    def construir_texto_bert(self, book_description="", review=""):
        """
        Se mantiene por compatibilidad con código anterior.
        Para sentimiento se recomienda usar solo review.
        """
        review = self.preparar_texto(review)
        return review

    def normalizar_label(self, label):
        label = str(label).lower().strip()

        mapa = {
            "negative": "Negativo",
            "neutral": "Neutral",
            "positive": "Positivo",
            "label_0": "Negativo",
            "label_1": "Neutral",
            "label_2": "Positivo",
            "0": "Negativo",
            "1": "Neutral",
            "2": "Positivo",
        }

        return mapa.get(label, "Neutral")

    def aplicar_heuristica_neutral(self, texto, sentimiento, probabilidades):
        """
        Ajuste conservador:
        Si el texto contiene expresiones claramente mixtas/neutrales
        y el modelo no está muy seguro, lo pasamos a Neutral.
        """
        if not self.aplicar_reglas_neutral:
            return sentimiento

        texto_lower = texto.lower()

        pistas_neutrales = [
            "it was okay",
            "was okay",
            "it's okay",
            "not great",
            "not bad",
            "not terrible",
            "average",
            "fine",
            "decent",
            "mixed feelings",
            "nothing special",
            "neither good nor bad",
            "so so",
            "just okay",
        ]

        contiene_pista = any(pista in texto_lower for pista in pistas_neutrales)

        if not contiene_pista:
            return sentimiento

        probs_ordenadas = sorted(
            probabilidades.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if len(probs_ordenadas) < 2:
            return sentimiento

        diferencia = probs_ordenadas[0][1] - probs_ordenadas[1][1]

        if diferencia <= 0.18:
            return "Neutral"

        return sentimiento

    def _predecir_batch_interno(self, textos):
        textos_limpios = [self.preparar_texto(texto) for texto in textos]

        inputs = self.tokenizer(
            textos_limpios,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.max_length,
        )

        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        probs = probs.detach().cpu().tolist()

        resultados = []

        for texto, probas in zip(textos_limpios, probs):
            probabilidades_es = {}

            for idx, probabilidad in enumerate(probas):
                label_modelo = self.id2label.get(idx, f"LABEL_{idx}")
                label_es = self.normalizar_label(label_modelo)
                probabilidades_es[label_es] = round(float(probabilidad), 4)

            # Garantiza las 3 claves aunque el modelo use nombres raros.
            for etiqueta in ["Negativo", "Neutral", "Positivo"]:
                probabilidades_es.setdefault(etiqueta, 0.0)

            sentimiento = max(probabilidades_es, key=probabilidades_es.get)
            score = probabilidades_es[sentimiento]

            sentimiento_ajustado = self.aplicar_heuristica_neutral(
                texto=texto,
                sentimiento=sentimiento,
                probabilidades=probabilidades_es,
            )

            resultado = {
                "texto": texto,
                "sentimiento": sentimiento_ajustado,
                "sentimiento_modelo": sentimiento,
                "score": round(float(probabilidades_es.get(sentimiento_ajustado, score)), 4),
                "probabilidades": {
                    "Negativo": round(float(probabilidades_es.get("Negativo", 0.0)), 4),
                    "Neutral": round(float(probabilidades_es.get("Neutral", 0.0)), 4),
                    "Positivo": round(float(probabilidades_es.get("Positivo", 0.0)), 4),
                },
            }

            resultados.append(resultado)

        return resultados

    def predecir_texto(self, texto):
        texto = self.preparar_texto(texto)

        if texto == "":
            return {"error": "El texto está vacío."}

        return self._predecir_batch_interno([texto])[0]

    def predecir_review(self, review):
        texto = self.construir_texto_bert(review=review)
        return self.predecir_texto(texto)

    def predecir_descripcion_y_review(self, book_description, review):
        texto = self.construir_texto_bert(
            book_description=book_description,
            review=review,
        )
        return self.predecir_texto(texto)

    def predecir_lote(self, textos, batch_size=None):
        if not textos:
            return []

        batch_size = batch_size or self.batch_size

        textos_preparados = [self.preparar_texto(texto) for texto in textos]
        resultados_finales = [None] * len(textos_preparados)

        indices_validos = []
        textos_validos = []

        for idx, texto in enumerate(textos_preparados):
            if texto != "":
                indices_validos.append(idx)
                textos_validos.append(texto)

        if not textos_validos:
            return []

        total = len(textos_validos)

        for inicio in range(0, total, batch_size):
            fin = inicio + batch_size
            batch_textos = textos_validos[inicio:fin]
            batch_indices = indices_validos[inicio:fin]

            resultados_batch = self._predecir_batch_interno(batch_textos)

            for idx_original, resultado in zip(batch_indices, resultados_batch):
                resultados_finales[idx_original] = resultado

            procesados = min(fin, total)

            #if procesados % 500 == 0 or procesados == total:
             #   print(f"Predicciones procesadas: {procesados}/{total}")

        return [resultado for resultado in resultados_finales if resultado is not None]

    def predecir_dataframe(
        self,
        df,
        columna_texto="texto_bert",
        columna_salida="sentimiento_predicho",
        batch_size=None,
    ):
        if columna_texto not in df.columns:
            raise ValueError(f"No existe la columna '{columna_texto}' en el DataFrame.")

        df = df.copy()
        df[columna_texto] = df[columna_texto].fillna("").astype(str).str.strip()
        df = df[df[columna_texto] != ""].copy()

        resultados = self.predecir_lote(
            textos=df[columna_texto].tolist(),
            batch_size=batch_size,
        )

        df[columna_salida] = [r["sentimiento"] for r in resultados]
        df["sentimiento_score"] = [r["score"] for r in resultados]
        df["prob_negativo"] = [r["probabilidades"]["Negativo"] for r in resultados]
        df["prob_neutral"] = [r["probabilidades"]["Neutral"] for r in resultados]
        df["prob_positivo"] = [r["probabilidades"]["Positivo"] for r in resultados]

        return df


def probar_predictor():
    predictor = PredictorSentimientos()

    ejemplos = [
        "I loved this book. It was amazing, emotional and beautifully written.",
        "This book was boring, slow and very disappointing. I did not enjoy it.",
        "It was okay, not great but not terrible either.",
    ]

    print("\n=== PRUEBAS DE PREDICCIÓN ===")

    for ejemplo in ejemplos:
        resultado = predictor.predecir_review(ejemplo)
        print("\nReview:", ejemplo)
        print("Resultado:", resultado)


if __name__ == "__main__":
    probar_predictor()
