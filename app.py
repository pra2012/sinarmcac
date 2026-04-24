import streamlit as st
import pandas as pd
import pandas as pd
import datetime
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Portal de Reclamações SINARM/CAC", layout="wide")

# Título e Estilo
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { background-color: #e74c3c; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Portal de Reclamações SINARM/CAC")
st.subheader("Transparência e Monitoramento de Prazos Legais")

# --- BANCO DE DADOS (CSV) ---
DB_FILE = "reclamacoes.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, parse_dates=['data_inicio'])
    return pd.DataFrame(columns=['protocolo', 'tipo', 'data_inicio', 'regiao', 'dias_espera'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# Carregar dados existentes
df_reclamacoes = load_data()

# --- INTERFACE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📝 Registrar Reclamação")
    with st.form("form_reclamacao", clear_on_submit=True):
        protocolo = st.text_input("Número do Protocolo (Ex: 991810...)")
        tipo = st.selectbox("Tipo de Processo", ["Aquisição", "Registro (CRAF)", "Transferência", "Porte", "Guia de Tráfego"])
        data_inicio = st.date_input("Data de Início do Processo", max_value=datetime.date.today())
        regiao = st.selectbox("Região/UF", ["Sul", "Sudeste", "Centro-Oeste", "Nordeste", "Norte"])
        
        submitted = st.form_submit_button("Protocolar Reclamação")
        
        if submitted:
            if protocolo:
                # Calcular dias de espera
                hoje = datetime.date.today()
                dias = (hoje - data_inicio).days
                
                # Novo registro
                nova_reclamacao = {
                    'protocolo': protocolo,
                    'tipo': tipo,
                    'data_inicio': data_inicio,
                    'regiao': regiao,
                    'dias_espera': dias
                }
                
                # Atualizar banco de dados
                df_reclamacoes = pd.concat([df_reclamacoes, pd.DataFrame([nova_reclamacao])], ignore_index=True)
                save_data(df_reclamacoes)
                st.success("Reclamação registrada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o número do protocolo.")

with col2:
    st.markdown("### 📊 Tempo Médio de Espera por Região")
    
    if not df_reclamacoes.empty:
        # Agrupar dados para o gráfico
        df_grafico = df_reclamacoes.groupby('regiao')['dias_espera'].mean().reset_index()
        
        fig = px.bar(df_grafico, x='regiao', y='dias_espera', 
                     text_auto=True,
                     title="Média de Dias para Análise",
                     labels={'dias_espera': 'Dias de Atraso', 'regiao': 'Região'},
                     color_discrete_sequence=['#2c3e50'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Últimas Reclamações")
        st.dataframe(df_reclamacoes.tail(10), use_container_width=True)
    else:
        st.info("Ainda não há dados cadastrados. Seja o primeiro a registrar!")

# Rodapé
st.markdown("---")
st.caption("Atenção: Este portal utiliza a Lei 9.784/99 como base para monitoramento de prazos administrativos.")
