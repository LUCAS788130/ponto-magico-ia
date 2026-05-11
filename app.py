import streamlit as st
import pandas as pd

from extractor import analisar_pdf
from ai_parser import configurar_openrouter, interpretar_cartao_com_ia
from validator import validar_dados
from exporter import gerar_csv, gerar_csv_pjecalc


st.set_page_config(
    page_title="Ponto Mágico IA",
    page_icon="🕒",
    layout="wide"
)


st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}

.titulo {
    font-size: 34px;
    font-weight: 800;
    color: #f8fafc;
    text-align: center;
    margin-bottom: 8px;
}

.subtitulo {
    font-size: 17px;
    color: #cbd5e1;
    text-align: center;
    margin-bottom: 30px;
}

.info-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="titulo">🕒 Ponto Mágico IA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Converta cartões de ponto em PDF para CSV estruturado com auxílio de IA.</div>',
    unsafe_allow_html=True
)


try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
    configurar_openrouter(api_key)
except Exception:
    st.error("Configure a chave OPENROUTER_API_KEY em Settings → Secrets no Streamlit.")
    st.stop()


if "df_resultado" not in st.session_state:
    st.session_state.df_resultado = None

if "tipo_pdf" not in st.session_state:
    st.session_state.tipo_pdf = None


arquivo_pdf = st.file_uploader(
    "Enviar cartão de ponto em PDF",
    type=["pdf"]
)


if arquivo_pdf:
    processar = st.button(
        "🚀 Processar com IA",
        use_container_width=True
    )

    if processar:
        try:
            with st.spinner("Analisando PDF..."):
                analise = analisar_pdf(arquivo_pdf)

            texto = analise["texto"]
            imagens = analise["imagens"]
            tipo = analise["tipo"]

            st.session_state.tipo_pdf = tipo

            with st.spinner("A IA está identificando o layout e extraindo as marcações..."):
                dados_ia = interpretar_cartao_com_ia(texto, imagens)

            dados_validados = validar_dados(dados_ia)
            st.session_state.df_resultado = pd.DataFrame(dados_validados)

            st.success(f"Cartão processado com sucesso. Tipo detectado: {tipo}")

        except Exception as erro:
            st.error(str(erro))


if st.session_state.df_resultado is not None:
    st.markdown("## Conferência das marcações")

    if st.session_state.tipo_pdf:
        st.info(f"Tipo de PDF detectado: {st.session_state.tipo_pdf}")

    df_editado = st.data_editor(
        st.session_state.df_resultado,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )

    st.session_state.df_resultado = df_editado

    if "Alerta" in df_editado.columns:
        alertas = df_editado[df_editado["Alerta"].astype(str).str.strip() != ""]

        if not alertas.empty:
            st.warning("Existem dias com inconsistências. Confira antes de gerar o CSV.")
            st.dataframe(alertas, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        csv_simples = gerar_csv(df_editado)

        st.download_button(
            label="⬇️ Baixar CSV simples",
            data=csv_simples,
            file_name="cartao_ponto.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        csv_pjecalc = gerar_csv_pjecalc(df_editado)

        st.download_button(
            label="⬇️ Baixar CSV PJe-Calc",
            data=csv_pjecalc,
            file_name="cartao_ponto_pjecalc.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("Envie um PDF para iniciar.")
