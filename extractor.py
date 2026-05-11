import fitz
from PIL import Image
import io


def analisar_pdf(arquivo_pdf):
    """
    Analisa se o PDF tem texto pesquisável ou se é digitalizado.
    Retorna texto, imagens e tipo detectado.
    """
    arquivo_pdf.seek(0)
    pdf_bytes = arquivo_pdf.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    texto_total = ""
    imagens = []

    for pagina in doc:
        texto_pagina = pagina.get_text("text") or ""
        texto_total += texto_pagina + "\n"

    texto_limpo = texto_total.strip()

    # Se tiver pouco texto, considera digitalizado
    pdf_digitalizado = len(texto_limpo) < 300

    # Para IA visual, sempre converte em imagem.
    # Limite será tratado no ai_parser.py
    for pagina in doc:
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        imagem = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        imagens.append(imagem)

    return {
        "texto": texto_limpo,
        "imagens": imagens,
        "tipo": "DIGITALIZADO" if pdf_digitalizado else "PESQUISAVEL"
    }
