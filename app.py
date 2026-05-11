import streamlit as st
import pandas as pd

from extractor import extrair_texto_pdf, converter_pdf_em_imagens
from ai_parser import configurar_gemini, interpretar_cartao_com_ia
from validator import validar_dados
from exporter import gerar_csv, gerar_csv_pjecalc


st.set_page_config(
    page_title="Conversor Inteligente de Cartão de Ponto",
    page_icon="🕒",
    layout="wide"
)


st.markdown("""
<style>
.main {
    background-color: #0f172a;
}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

.card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 20px;
}

.titulo {
    font-size: 34px;
    font-weight: 800;
    color: #f8fafc;
    text-align: center;
}

.subtitulo {
    font-size: 17px;
    color: #cbd5e1;
    text-align: center;
    margin-bottom: 30px;
}

.alerta {
    background: #451a1a;
    border: 1px solid #dc2626;
    color: #fecaca;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="titulo">🕒 Conversor Inteligente de Cartão de Ponto</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo">Envie o PDF, revise as marcações e gere o CSV para utilização posterior.</div>',
    unsafe_allow_html=True
)


try:
    api_key = st.secrets["GEMINI_API_KEY"]
    configurar_gemini(api_key)
except Exception:
    st.error("Configure a chave GEMINI_API_KEY no arquivo .streamlit/secrets.toml.")
    st.stop()


arquivo_pdf = st.file_uploader(
    "Enviar cartão de ponto em PDF",
    type=["pdf"]
)


if "df_resultado" not in st.session_state:
    st.session_state.df_resultado = None


if arquivo_pdf:
    col1, col2 = st.columns([1, 1])

    with col1:
        usar_imagem = st.checkbox(
            "Usar imagens do PDF na análise da IA",
            value=True,
            help="Recomendado para PDFs digitalizados ou com OCR ruim."
        )

    with col2:
        processar = st.button("🚀 Processar com IA", use_container_width=True)

    if processar:
        with st.spinner("Lendo PDF..."):
            texto = extrair_texto_pdf(arquivo_pdf)

        imagens = None

        if usar_imagem:
            with st.spinner("Convertendo páginas em imagem..."):
                imagens = converter_pdf_em_imagens(arquivo_pdf)

        with st.spinner("A IA está interpretando o cartão de ponto..."):
            try:
                dados_ia = interpretar_cartao_com_ia(texto, imagens)
                dados_validados = validar_dados(dados_ia)
                st.session_state.df_resultado = pd.DataFrame(dados_validados)
                st.success("Cartão processado com sucesso.")
            except Exception as erro:
                st.error(str(erro))


if st.session_state.df_resultado is not None:
    st.markdown("## Conferência das marcações")

    df_editado = st.data_editor(
        st.session_state.df_resultado,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )

    st.session_state.df_resultado = df_editado

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
