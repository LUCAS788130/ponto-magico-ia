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
Você é especialista em cartões de ponto brasileiros.

Extraia APENAS datas e marcações reais de ponto.

Regras:
1. Identifique automaticamente o layout.
2. Extraia apenas horários reais de entrada e saída.
3. Priorize colunas chamadas:
   - Marcação ou Situação Funcional
   - Marcações
   - Horários
   - Registro de ponto
   - Batidas
4. Ignore completamente:
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
5. Não invente horários.
6. Dias sem marcação devem retornar lista vazia.
7. Ordene os horários em ordem crescente.
8. Retorne SOMENTE JSON válido, sem markdown.

Formato obrigatório:
[
  {
    "data": "01/05/2026",
    "marcacoes": ["07:00", "11:00", "13:00", "17:00"]
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
        for imagem in imagens[:4]:
            base64_image = imagem_para_base64(imagem)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
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
        raise Exception(
            f"""
Não foi possível processar com o roteador gratuito do OpenRouter.

Possíveis causas:
- limite gratuito atingido;
- nenhum modelo gratuito com visão disponível no momento;
- PDF muito grande;
- resposta da IA fora do JSON.

Último erro:
{erro}
"""
        )
