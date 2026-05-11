import json
import base64
import io
from openai import OpenAI


client = None


def configurar_openrouter(api_key):
    global client

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://share.streamlit.io",
            "X-Title": "Ponto Magico IA"
        }
    )


def imagem_para_base64(imagem):
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def limpar_json(texto):
    texto = str(texto).strip()

    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()

    if texto.startswith("```"):
        texto = texto.replace("```", "").strip()

    inicio = texto.find("[")
    fim = texto.rfind("]")

    if inicio != -1 and fim != -1:
        texto = texto[inicio:fim + 1]

    return texto


def interpretar_cartao_com_ia(texto_pdf, imagens=None):
    if client is None:
        raise Exception("Cliente OpenRouter não configurado.")

    prompt = """
Você é especialista em cartões de ponto brasileiros e em conversão para CSV.

OBJETIVO:
Extrair APENAS datas e marcações reais de ponto.

REGRAS OBRIGATÓRIAS:
1. Identifique automaticamente o layout do cartão de ponto.
2. Detecte se o documento é pesquisável ou digitalizado.
3. Extraia somente horários reais de entrada e saída.
4. Priorize colunas chamadas:
   - Marcação ou Situação Funcional
   - Marcações
   - Horários
   - Registro de ponto
   - Batidas
5. Ignore completamente colunas ou textos como:
   - H.E 50%
   - H.E 100%
   - H.NEG
   - Horas Extras
   - Banco de horas
   - Totais
   - Saldo
   - Observações
   - Jornada
   - Carga horária
   - Atrasos
   - Faltas
6. Não invente horários.
7. Se o dia não tiver marcação, retorne lista vazia.
8. Ordene os horários em ordem crescente.
9. Preserve todas as datas encontradas no cartão.
10. Retorne SOMENTE JSON válido.
11. Não escreva explicações.
12. Não use markdown.

FORMATO OBRIGATÓRIO:
[
  {
    "data": "01/05/2026",
    "marcacoes": ["07:00", "11:00", "13:00", "17:00"]
  },
  {
    "data": "02/05/2026",
    "marcacoes": []
  }
]
"""

    content = [
        {
            "type": "text",
            "text": prompt + "\n\nTexto extraído do PDF:\n" + (texto_pdf or "")
        }
    ]

    if imagens:
        # Limita para evitar excesso no modelo gratuito
        for imagem in imagens[:6]:
            base64_image = imagem_para_base64(imagem)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

    modelos = [
        "qwen/qwen2.5-vl-72b-instruct:free",
        "qwen/qwen-2.5-vl-7b-instruct:free"
    ]

    ultimo_erro = None

    for modelo in modelos:
        try:
            response = client.chat.completions.create(
                model=modelo,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0
            )

            resposta = response.choices[0].message.content
            texto_limpo = limpar_json(resposta)

            return json.loads(texto_limpo)

        except Exception as erro:
            ultimo_erro = erro
            continue

    raise Exception(
        f"""
Não foi possível processar com os modelos gratuitos do OpenRouter.

Possíveis causas:
- modelo gratuito indisponível no momento;
- limite gratuito atingido;
- PDF muito grande;
- resposta da IA fora do JSON.

Último erro:
{ultimo_erro}
"""
    )
