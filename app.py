import streamlit as st
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
    .stButton>button { background-color: #e74c3c; color: white; width: 100%; border-radius: 5px; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Portal de Reclamações SINARM/CAC")
st.subheader("Monitoramento de Prazos e Gestão de Reclamações")

# --- BANCO DE DADOS (CSV) ---
DB_FILE = "reclamacoes_detalhadas.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, parse_dates=['data_protocolo'])
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DB_FILE, index=False)

df_reclamacoes = load_data()

# --- INTERFACE ---
col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.markdown("### 📝 Registrar Reclamação")
    with st.form("form_detalhado", clear_on_submit=True):
        # Identificação
        nome = st.text_input("Nome Completo do Solicitante*")
        cpf = st.text_input("CPF*")
        email = st.text_input("Email para encaminhar tramitação*")
        
        # Dados do Processo
        protocolo = st.text_input("Número do Protocolo SINARMCAC/SISGCORP*")
        tipo = st.selectbox("Tipo de Processo", ["Aquisição", "Registro (CRAF)", "Transferência", "Porte", "Guia de Tráfego", "Renovação"])
        data_protocolo = st.date_input("Data do protocolo (data da compensação da GRU)*", max_value=datetime.date.today())
        
        # Localização e Responsáveis
        delegacia = st.text_input("Delegacia de Vinculação (Veja no seu CR)*")
        estado = st.selectbox("Estado da DELEARM (UF)*", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        cidade = st.text_input("Cidade da Sede da DELEARM*")
        servidor = st.text_input("Nome do Delegado ou Servidor Envolvido (se conhecido)")
        
        # Descrição
        relato = st.text_area("Relato Detalhado do Problema*")
        
        submitted = st.form_submit_button("Protocolar Reclamação")
        
        if submitted:
            if all([nome, cpf, email, protocolo, relato]):
                hoje = datetime.date.today()
                dias = (hoje - data_protocolo).days
                
                novo_registro = {
                    'nome': nome,
                    'cpf': cpf,
                    'email': email,
                    'protocolo': protocolo,
                    'tipo': tipo,
                    'data_protocolo': data_protocolo,
                    'dias_espera': dias,
                    'delegacia': delegacia,
                    'estado': estado,
                    'cidade': cidade,
                    'servidor': servidor,
                    'relato': relato
                }
                
                df_reclamacoes = pd.concat([df_reclamacoes, pd.DataFrame([novo_registro])], ignore_index=True)
                save_data(df_reclamacoes)
                st.success("Reclamação registrada! Os dados foram salvos.")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")

with col2:
    st.markdown("### 📊 Estatísticas e Transparência")
    
    if not df_reclamacoes.empty:
        # Gráfico por Estado
        df_grafico = df_reclamacoes.groupby('estado')['dias_espera'].mean().reset_index()
        fig = px.bar(df_grafico, x='estado', y='dias_espera', 
                     text_auto=True,
                     title="Média de Dias de Atraso por UF",
                     labels={'dias_espera': 'Dias Decorridos', 'estado': 'Estado'},
                     color_discrete_sequence=['#2c3e50'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Histórico Recente")
        # Mostrar apenas colunas públicas por segurança
        view_df = df_reclamacoes[['protocolo', 'tipo', 'estado', 'dias_espera']].tail(10)
        st.table(view_df)
    else:
        st.info("Aguardando os primeiros registros para gerar o gráfico.")

st.markdown("---")
st.caption("Base legal: Lei 9.784/99 e prazos regulamentares da Polícia Federal e Exército Brasileiro.")
