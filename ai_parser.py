import json
import google.generativeai as genai


def configurar_gemini(api_key):
    genai.configure(api_key=api_key)


def limpar_json(resposta):
    texto = resposta.strip()

    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()

    if texto.startswith("```"):
        texto = texto.replace("```", "").strip()

    return texto


def interpretar_cartao_com_ia(texto_pdf, imagens=None):
    """
    Usa IA Gemini para interpretar cartão de ponto.
    Tenta modelos diferentes caso algum esteja indisponível ou sem cota.
    """

    modelos = [
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash"
    ]

    prompt = """
Você é um especialista em interpretação de cartões de ponto brasileiros.

OBJETIVO:
Extrair APENAS as marcações reais de entrada e saída.

REGRAS:
1. Identifique todas as datas do cartão.
2. Extraia somente horários reais de marcação.
3. Considere principalmente a coluna:
   - Marcação ou Situação Funcional
   - Marcações
   - Horários
   - Registro de ponto
4. Ignore completamente:
   - H.E 50%
   - H.E 100%
   - H.NEG
   - Horas Extras
   - Banco de horas
   - Saldo
   - Observações
   - Totais
   - Adicionais
5. NÃO invente horários.
6. Se não houver marcação no dia, retorne lista vazia.
7. Ordene os horários cronologicamente.
8. Retorne SOMENTE JSON válido.
9. Não escreva explicações.
10. Não use markdown.

Formato obrigatório:

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

Texto extraído do PDF:
"""

    conteudo = [prompt + "\n\n" + (texto_pdf or "")]

    if imagens:
        conteudo.extend(imagens)

    ultimo_erro = None

    for nome_modelo in modelos:
        try:
            model = genai.GenerativeModel(nome_modelo)
            resposta = model.generate_content(conteudo)

            texto_resposta = limpar_json(resposta.text)

            dados = json.loads(texto_resposta)

            return dados

        except Exception as erro:
            ultimo_erro = erro
            continue

    raise Exception(
        f"""
Não foi possível processar com nenhum modelo Gemini disponível.

Possíveis causas:
- cota gratuita zerada;
- modelo indisponível;
- excesso de imagens/páginas;
- resposta da IA fora do formato JSON.

Último erro:

{ultimo_erro}
"""
    )
