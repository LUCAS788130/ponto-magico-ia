import fitz
from PIL import Image
import io


def extrair_texto_pdf(arquivo_pdf):
    """
    Tenta extrair texto direto do PDF.
    Funciona bem para PDFs pesquisáveis.
    """
    texto_total = ""

    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")

    for pagina in doc:
        texto_total += pagina.get_text("text") + "\n"

    return texto_total.strip()


def converter_pdf_em_imagens(arquivo_pdf):
    """
    Converte o PDF em imagens para análise pela IA.
    """
    arquivo_pdf.seek(0)
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")

    imagens = []

    for pagina in doc:
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        imagem = Image.open(io.BytesIO(img_bytes))
        imagens.append(imagem)

    return imagens
