import io


def gerar_csv(df):
    colunas = ["Data", "Entrada 1", "Saída 1", "Entrada 2", "Saída 2"]

    df_export = df[colunas].copy()

    buffer = io.StringIO()
    df_export.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")

    return buffer.getvalue()


def gerar_csv_pjecalc(df):
    """
    Modelo base.
    Quando você mandar o CSV exato aceito pelo PJe-Calc,
    ajustamos esta função no padrão definitivo.
    """
    colunas = ["Data", "Entrada 1", "Saída 1", "Entrada 2", "Saída 2"]

    df_export = df[colunas].copy()

    df_export = df_export.rename(columns={
        "Data": "DATA",
        "Entrada 1": "ENTRADA_1",
        "Saída 1": "SAIDA_1",
        "Entrada 2": "ENTRADA_2",
        "Saída 2": "SAIDA_2"
    })

    buffer = io.StringIO()
    df_export.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")

    return buffer.getvalue()
