import streamlit as st
import pandas as pd
from anthropic import Anthropic
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="WeConnectAi Suite", page_icon="🛠️", layout="wide")

# --- API SETUP ---
try:
    # Use the secret stored in Streamlit Cloud
    client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
except Exception as e:
    st.error("❌ API Key missing or invalid! Please add ANTHROPIC_API_KEY to Streamlit Secrets.")
    st.stop()

# --- NAVIGATION (The Hub) ---
st.sidebar.title("WeConnectAi Suite")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Escolha a Ferramenta:",
    ["Home", "myaitools (Análise Orçamentos)", "Tool 2 (Futuro)", "Tool 3 (Futuro)", "Tool 4 (Futuro)"])

if app_mode == "Home":
    st.title("🚀 Welcome to WeConnectAi Suite")
    st.write("Sonia, seja bem-vinda ao seu centro de ferramentas de engenharia.")
    st.info("Selecione 'myaitools' no menu lateral para começar a análise de orçamentos.")

    st.markdown("""
    ### 🛠️ Ferramentas Disponíveis:
    - **myaitools**: Auditoria de preços e análise crítica de orçamentos.
    - **Tool 2**: Em desenvolvimento...
    - **Tool 3**: Em desenvolvimento...
    - **Tool 4**: Em desenvolvimento...
    """)

elif app_mode == "myaitools (Análise Orçamentos)":
    st.title("🛠️ myaitools - Análise Crítica")
    st.write("Upload do ficheiro Excel para análise de custos e auditoria técnica.")

    uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("### 📄 Pré-visualização dos Dados")
            st.dataframe(df.head())

            if st.button("🚀 Processar com AI"):
                with st.spinner("A analisar com Claude AI... Aguarde a auditoria completa."):
                    # --- 1. NUMERICAL LOGIC (The 7 Columns) ---
                    res_df = df.copy()

                    # Calculations
                    res_df['PREÇO PRODUTO (mercado s/IVA)'] = res_df['V. UNIT.'] * 1.1
                    res_df['V. PARCIAL (mercado)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * res_df['QUANT.']
                    res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * 0.95
                    res_df['V. PARCIAL (competitivo)'] = res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] * res_df['QUANT.']
                    res_df['% M/O no preço compet.'] = 0.30
                    res_df['DIFERENÇA UNIT. orig - compet.'] = res_df['V. UNIT.'] - res_df['PREÇO COMPETITIVO (prod + M/O simult.)']
                    res_df['LINK DE ACESSO'] = "Ref: Mercado Algarve / Grossistas Profissionais"

                    # --- 2. AI CRITICAL ANALYSIS ---
                    budget_str = res_df.to_string()

                    prompt = f"""
                    You are a Senior Civil Engineering Auditor in the Algarve, Portugal.
                    Analyze the following budget data. Create a detailed 'ANÁLISE CRÍTICA DO ORÇAMENTO'
                    following this exact structure:
                    1. CONTEXTO: Explain that mobilization is 0€ as the team is already on site.
                    2. MATERIAIS DE ENCHIMENTO: Identify excesses in items like Leca, Terra Vegetal, etc.
                    3. PLANTAS: Analyze professional wholesale prices (FlorAccess).
                    4. EXCEÇÕES NOTÁVEIS: Find items with fair or low prices.
                    5. ECONOMIA DE ESCALA: Note the volume of materials and lack of discounts.
                    6. SÍNTESE FINANCEIRA: Total original vs Total competitive and a clear Negotiation Strategy.

                    Budget Data:
                    {budget_str}
                    """

                    message = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    # BRUTE FORCE FIX: Extract only text, ignoring all ThinkingBlocks
                    analysis_text = ""
                    for block in message.content:
                        try:
                            # The only blocks we want are those with the .text attribute
                            analysis_text += block.text
                        except AttributeError:
                            # This skips ThinkingBlocks and other non-text elements
                            continue

                    if not analysis_text.strip():
                        analysis_text = "Erro: O modelo gerou apenas raciocínio interno e nenhum texto final."

                    # --- 3. EXPORT TO EXCEL ---
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_df.to_excel(writer, sheet_name='Analise Quantitativa', index=False)
                        analysis_df = pd.DataFrame({'Relatorio de Auditoria': [analysis_text]})
                        analysis_df.to_excel(writer, sheet_name='Analise Critica', index=False)

                    st.success("✅ Análise concluída com sucesso!")

                    st.download_button(
                        label="📥 Download Result Analysis (Excel)",
                        data=output.getvalue(),
                        file_name="Analise_Critica_myaitools.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.markdown("---")
                    st.write("### 📝 Relatório Preliminar da AI:")
                    st.info(analysis_text)

        except Exception as e:
            st.error(f"Erro no processamento do arquivo: {e}")

# For Tools 2, 3, 4
else:
    st.title(app_mode)
    st.warning("Esta ferramenta está atualmente em desenvolvimento e será integrada em breve.")