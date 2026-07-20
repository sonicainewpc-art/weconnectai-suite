import streamlit as st
import pandas as pd
from anthropic import Anthropic
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="WeConnectAi Suite", page_icon="🛠️", layout="wide")

# --- API SETUP ---
try:
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
                with st.spinner("A analisar com Claude 4.5 Sonnet..."):
                    res_df = df.copy()

                    # Calculations
                    res_df['PREÇO PRODUTO (mercado s/IVA)'] = res_df['V. UNIT.'] * 1.1
                    res_df['V. PARCIAL (mercado)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * res_df['QUANT.']
                    res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * 0.95
                    res_df['V. PARCIAL (competitivo)'] = res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] * res_df['QUANT.']
                    res_df['% M/O no preço compet.'] = 0.30
                    res_df['DIFERENÇA UNIT. orig - compet.'] = res_df['V. UNIT.'] - res_df['PREÇO COMPETITIVO (prod + M/O simult.)']
                    res_df['LINK DE ACESSO'] = "Ref: Mercado Algarve / Grossistas Profissionais"

                    budget_str = res_df.to_string()
                    prompt = f"Analyze this budget for the Algarve, Portugal. Use sections: CONTEXTO (mobilization 0€), MATERIAIS, PLANTAS (FlorAccess), EXCEÇÕES, ESCALA and SÍNTESE FINANCEIRA. Budget:\n{budget_str}"

                    # --- USING YOUR EXACT 4.5 MODEL IDs ---
                    # We prioritize Sonnet 4.5, then Opus 4.5, then Haiku 4.5
                    models_to_try = ["claude-sonnet-4-5-20250929", "claude-opus-4-5-20251001", "claude-haiku-4-5-20251001"]
                    analysis_text = ""
                    used_model = ""

                    for model_name in models_to_try:
                        try:
                            message = client.messages.create(
                                model=model_name,
                                max_tokens=4000,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            for block in message.content:
                                try: analysis_text += block.text
                                except AttributeError: continue

                            used_model = model_name
                            break
                        except Exception:
                            continue

                    if not analysis_text:
                        st.error("❌ Erro: Nenhum dos modelos 4.5 foi aceito. Verifique a sua chave API.")
                        st.stop()

                    # --- EXPORT TO EXCEL ---
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_df.to_excel(writer, sheet_name='Analise Quantitativa', index=False)
                        analysis_df = pd.DataFrame({'Relatorio de Auditoria': [analysis_text]})
                        analysis_df.to_excel(writer, sheet_name='Analise Critica', index=False)

                    st.success(f"✅ Análise concluída com sucesso usando: {used_model}")

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

else:
    st.title(app_mode)
    st.warning("Esta ferramenta está atualmente em desenvolvimento.")