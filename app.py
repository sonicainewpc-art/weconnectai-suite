import streamlit as st
import pandas as pd
from anthropic import Anthropic
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="WeConnectAi Suite", page_icon="🛠️", layout="wide")

# --- API SETUP ---
# This looks for the key in the 'Secrets' section of Streamlit
try:
    client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
except:
    st.error("API Key missing! Please add ANTHROPIC_API_KEY to Streamlit Secrets.")

# --- NAVIGATION (The Hub) ---
st.sidebar.title("WeConnectAi Suite")
app_mode = st.sidebar.selectbox("Escolha a Ferramenta:",
    ["Home", "myaitools (Análise Orçamentos)", "Tool 2 (Futuro)", "Tool 3 (Futuro)", "Tool 4 (Futuro)"])

if app_mode == "Home":
    st.title("🚀 Welcome to WeConnectAi Suite")
    st.write("Selecione uma ferramenta no menu lateral para começar.")
    st.image("https://via.placeholder.com/800x400?text=WeConnectAi+Business+Solutions")

elif app_mode == "myaitools (Análise Orçamentos)":
    st.title("🛠️ myaitools - Análise Crítica")
    st.write("Upload do ficheiro Excel para análise de custos e auditoria.")

    uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("### Pré-visualização dos Dados")
        st.dataframe(df.head())

        if st.button("Processar com AI"):
            with st.spinner("A analisar com Claude AI..."):
                try:
                    # 1. Calculate the 7 columns
                    df['PREÇO PRODUTO (mercado s/IVA)'] = df['V. UNIT.'] * 1.1
                    df['V. PARCIAL (mercado)'] = df['PREÇO PRODUTO (mercado s/IVA)'] * df['QUANT.']
                    df['PREÇO COMPETITIVO (prod + M/O simult.)'] = df['PREÇO PRODUTO (mercado s/IVA)'] * 0.95
                    df['V. PARCIAL (competitivo)'] = df['PREÇO COMPETITIVO (prod + M/O simult.)'] * df['QUANT.']
                    df['% M/O no preço compet.'] = 0.30
                    df['DIFERENÇA UNIT. orig - compet.'] = df['V. UNIT.'] - df['PREÇO COMPETITIVO (prod + M/O simult.)']
                    df['LINK DE ACESSO'] = "https://weconnectai.pt"

                    # 2. Generate Critical Analysis
                    budget_str = df.to_string()
                    prompt = f"Analyze this budget as a Senior Civil Engineering Auditor in Portugal. Use the specific sections: CONTEXTO, MATERIAIS, PLANTAS, EXCEÇÕES, ESCALA and SÍNTESE FINANCEIRA. Budget:\n{budget_str}"

                    message = client.messages.create(
                        model="claude-sonnet-5",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    analysis_text = message.content[0].text

                    # 3. Export to Excel with 2 sheets
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Analise Quantitativa', index=False)
                        analysis_df = pd.DataFrame({'Relatorio': [analysis_text]})
                        analysis_df.to_excel(writer, sheet_name='Analise Critica', index=False)

                    st.success("Análise concluída!")
                    st.download_button(
                        label="📥 Download Result Analysis",
                        data=output.getvalue(),
                        file_name="Analise_myaitools.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.write("### Relatório AI:")
                    st.info(analysis_text)

                except Exception as e:
                    st.error(f"Erro no processamento: {e}")

# For Tools 2, 3, 4
else:
    st.title(app_mode)
    st.write("Esta ferramenta ainda está em desenvolvimento.")