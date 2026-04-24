import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Portal de Reclamações SINARM/CAC", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { background-color: #e74c3c; color: white; width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Portal de Reclamações SINARM/CAC")

# --- INFRAESTRUTURA DE DADOS ---
DB_FILE = "reclamacoes_detalhadas.csv"
UPLOAD_DIR = "anexos_provas"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DB_FILE, index=False)

df_reclamacoes = load_data()

# --- INTERFACE ---
col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.markdown("### 📝 Registrar Reclamação")
    with st.form("form_detalhado", clear_on_submit=True):
        st.info("Identificação e Processo")
        nome = st.text_input("Nome Completo do Solicitante*")
        protocolo = st.text_input("Número do Protocolo SINARMCAC/SISGCORP*")
        tipo = st.selectbox("Tipo de Processo", ["Aquisição", "Registro (CRAF)", "Transferência", "Porte", "Guia de Tráfego", "Renovação"])
        
        st.warning("⏱️ Cronologia de Pagamento (GRU)")
        # Data que o usuário efetivamente pagou no banco
        data_pagamento_real = st.date_input("Data do Pagamento Efetivo (conforme comprovante)*", max_value=datetime.date.today())
        # Data que apareceu como pago no sistema (SINARM/SISGCORP)
        data_compensacao_sistema = st.date_input("Data da Compensação no Sistema (Reconhecimento)*", max_value=datetime.date.today())
        
        st.info("Localização e Relato")
        estado = st.selectbox("Estado da DELEARM (UF)*", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        relato = st.text_area("Relato Detalhado do Problema*")
        
        arquivos_anexos = st.file_uploader(
            "Subir Comprovante de Pagamento da GRU e Prints*", 
            type=['png', 'jpg', 'jpeg', 'pdf'], 
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Protocolar Reclamação")
        
        if submitted:
            if all([nome, protocolo, relato]):
                hoje = datetime.date.today()
                
                # CÁLCULOS DE TEMPO
                # 1. Tempo para o sistema reconhecer o dinheiro (Eficiência Bancária/Sistêmica)
                tempo_reconhecimento = (data_compensacao_sistema - data_pagamento_real).days
                
                # 2. Tempo total de atraso após a compensação (Atraso Administrativo)
                atraso_pos_compensacao = (hoje - data_compensacao_sistema).days
                
                # Salvar arquivos
                caminhos_arquivos = []
                for idx, arquivo in enumerate(arquivos_anexos):
                    nome_seguro = f"{protocolo}_{idx}_{arquivo.name}"
                    with open(os.path.join(UPLOAD_DIR, nome_seguro), "wb") as f:
                        f.write(arquivo.getbuffer())
                    caminhos_arquivos.append(nome_seguro)
                
                novo_registro = {
                    'nome': nome,
                    'protocolo': protocolo,
                    'tipo': tipo,
                    'data_pagamento': data_pagamento_real,
                    'data_compensacao': data_compensacao_sistema,
                    'dias_para_reconhecer': tempo_reconhecimento,
                    'dias_atraso_adm': atraso_pos_compensacao,
                    'estado': estado,
                    'relato': relato,
                    'anexos': ", ".join(caminhos_arquivos)
                }
                
                df_reclamacoes = pd.concat([df_reclamacoes, pd.DataFrame([novo_registro])], ignore_index=True)
                save_data(df_reclamacoes)
                st.success("Dados registrados! Cálculo de compensação realizado.")
                st.rerun()

with col2:
    st.markdown("### 📊 Auditoria de Prazos")
    if not df_reclamacoes.empty:
        # Gráfico 1: Tempo Médio de Reconhecimento de Pagamento por UF
        df_recon = df_reclamacoes.groupby('estado')['dias_para_reconhecer'].mean().reset_index()
        fig1 = px.bar(df_recon, x='estado', y='dias_para_reconhecer', 
                     title="Tempo Médio para Sistema Reconhecer Pagamento (Dias)",
                     labels={'dias_para_reconhecer': 'Dias', 'estado': 'UF'},
                     color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Atraso Administrativo Pós-Compensação
        df_atraso = df_reclamacoes.groupby('estado')['dias_atraso_adm'].mean().reset_index()
        fig2 = px.bar(df_atraso, x='estado', y='dias_atraso_adm', 
                     title="Atraso Médio na Análise Pós-Compensação (Dias)",
                     labels={'dias_atraso_adm': 'Dias de Espera', 'estado': 'UF'},
                     color_discrete_sequence=['#e74c3c'])
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("### 📋 Resumo de Eficiência")
        st.dataframe(df_reclamacoes[['protocolo', 'estado', 'dias_para_reconhecer', 'dias_atraso_adm']].tail(10))
    else:
        st.info("Aguardando registros para análise estatística.")
