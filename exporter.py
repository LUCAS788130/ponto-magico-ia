import pandas as pd
import io


def gerar_csv(df):
    """
    Gera CSV simples.
    Depois podemos adaptar exatamente ao modelo do PJe-Calc.
    """
    colunas = ["Data", "Entrada 1", "Saída 1", "Entrada 2", "Saída 2"]

    df_export = df[colunas].copy()

    buffer = io.StringIO()
    df_export.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")

    return buffer.getvalue()


def gerar_csv_pjecalc(df):
    """
    Modelo base adaptável para o PJe-Calc.
    Se você mandar o CSV exato aceito pelo sistema, ajusto esta função.
    """
    linhas = []

    for _, row in df.iterrows():
        linhas.append({
            "DATA": row.get("Data", ""),
            "ENTRADA_1": row.get("Entrada 1", ""),
            "SAIDA_1": row.get("Saída 1", ""),
            "ENTRADA_2": row.get("Entrada 2", ""),
            "SAIDA_2": row.get("Saída 2", "")
        })

    df_final = pd.DataFrame(linhas)

    buffer = io.StringIO()
    df_final.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")

    return buffer.getvalue()
