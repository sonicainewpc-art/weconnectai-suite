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
                with st.spinner("A analisar... O sistema está a selecionar o melhor modelo disponível."):
                    res_df = df.copy()
                    res_df['PREÇO PRODUTO (mercado s/IVA)'] = res_df['V. UNIT.'] * 1.1
                    res_df['V. PARCIAL (mercado)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * res_df['QUANT.']
                    res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] = res_df['PREÇO PRODUTO (mercado s/IVA)'] * 0.95
                    res_df['V. PARCIAL (competitivo)'] = res_df['PREÇO COMPETITIVO (prod + M/O simult.)'] * res_df['QUANT.']
                    res_df['% M/O no preço compet.'] = 0.30
                    res_df['DIFERENÇA UNIT. orig - compet.'] = res_df['V. UNIT.'] - res_df['PREÇO COMPETITIVO (prod + M/O simult.)']
                    res_df['LINK DE ACESSO'] = "Ref: Mercado Algarve / Grossistas Profissionais"

                    budget_str = res_df.to_string()
                    prompt = f"Analyze this budget for the Algarve, Portugal. Use sections: CONTEXTO (mobilization 0€), MATERIAIS, PLANTAS (FlorAccess), EXCEÇÕES, ESCALA and SÍNTESE FINANCEIRA. Budget:\n{budget_str}"

                    # --- SMART MODEL SELECTION ---
                    # We try these in order: Newest Sonnet -> Older Sonnet -> Haiku (Guaranteed)
                    models_to_try = ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"]
                    analysis_text = ""
                    used_model = ""

                    for model_name in models_to_try:
                        try:
                            message = client.messages.create(
                                model=model_name,
                                max_tokens=4000,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            # Brute force extract text from blocks
                            for block in message.content:
                                try: analysis_text += block.text
                                except AttributeError: continue

                            used_model = model_name
                            break # Stop trying other models if this one works!
                        except Exception:
                            continue # Try the next model in the list

                    if not analysis_text:
                        st.error("❌ Todos os modelos falharam. Verifique o saldo de créditos da sua API Anthropic.")
                        st.stop()

                    # --- EXPORT TO EXCEL ---
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_df.to_excel(writer, sheet_name='Analise Quantitativa', index=False)
                        analysis_df = pd.DataFrame({'Relatorio de Auditoria': [analysis_text]})
                        analysis_df.to_excel(writer, sheet_name='Analise Critica', index=False)

                    st.success(f"✅ Análise concluída com sucesso usando o modelo: {used_model}")

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