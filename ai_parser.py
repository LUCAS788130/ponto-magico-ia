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
    Usa IA para interpretar cartão de ponto.
    Retorna lista de dias com marcações.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = """
Você é um assistente especializado em converter cartões de ponto para CSV do PJe-Calc.

Sua tarefa:
1. Identificar todos os dias do período.
2. Extrair APENAS as marcações reais de ponto.
3. Considerar prioritariamente a coluna chamada "Marcação ou Situação Funcional", "Marcações", "Horários" ou equivalente.
4. Ignorar colunas como:
   - H.E 50%
   - H.E 100%
   - H.NEG
   - Horas Extras
   - Total
   - Saldo
   - Banco de horas
   - Observações
   - Jornada
   - Carga horária
5. Não inventar horários.
6. Manter dias sem marcação com lista vazia.
7. Ordenar horários em ordem crescente.
8. Retornar exclusivamente JSON válido.

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

    resposta = model.generate_content(conteudo)
    texto_resposta = limpar_json(resposta.text)

    try:
        dados = json.loads(texto_resposta)
    except Exception as erro:
        raise ValueError(f"A IA não retornou JSON válido:\n\n{texto_resposta}") from erro

    return dados
