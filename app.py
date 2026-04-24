import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Portal de Reclamações SINARM/CAC", layout="wide")

# Estilização
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
        st.info("Identificação e Contato")
        nome = st.text_input("Nome Completo do Solicitante*")
        cpf = st.text_input("CPF*")
        email = st.text_input("Email para encaminhar tramitação*")
        
        st.info("Dados do Processo")
        protocolo = st.text_input("Número do Protocolo SINARMCAC/SISGCORP*")
        tipo = st.selectbox("Tipo de Processo", ["Aquisição", "Registro (CRAF)", "Transferência", "Porte", "Guia de Tráfego", "Renovação"])
        data_protocolo = st.date_input("Data do protocolo (compensação GRU)*", max_value=datetime.date.today())
        
        st.info("Localização")
        delegacia = st.text_input("Delegacia de Vinculação (Veja no seu CR)*")
        estado = st.selectbox("Estado da DELEARM (UF)*", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        cidade = st.text_input("Cidade da Sede da DELEARM*")
        servidor = st.text_input("Nome do Delegado/Servidor (se conhecido)")
        
        st.info("Relato e Provas")
        relato = st.text_area("Relato Detalhado do Problema*")
        
        # MÚLTIPLOS ARQUIVOS: O parâmetro 'accept_multiple_files' permite o upload em massa
        arquivos_anexos = st.file_uploader(
            "Anexo de Prova Documental (Selecione um ou mais arquivos)", 
            type=['png', 'jpg', 'jpeg', 'pdf'], 
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Protocolar Reclamação")
        
        if submitted:
            if all([nome, cpf, email, protocolo, relato]):
                hoje = datetime.date.today()
                dias = (hoje - data_protocolo).days
                
                # Processamento de cada arquivo subido
                caminhos_arquivos = []
                for idx, arquivo in enumerate(arquivos_anexos):
                    # Gera um nome único: PROTOCOLO_SEQUENCIA_NOMEARQUIVO
                    nome_seguro = f"{protocolo}_{idx}_{arquivo.name}"
                    file_path = os.path.join(UPLOAD_DIR, nome_seguro)
                    with open(file_path, "wb") as f:
                        f.write(arquivo.getbuffer())
                    caminhos_arquivos.append(nome_seguro)
                
                # Transforma a lista de arquivos em uma string separada por vírgulas para o CSV
                anexos_string = ", ".join(caminhos_arquivos)
                
                novo_registro = {
                    'nome': nome, 'cpf': cpf, 'email': email,
                    'protocolo': protocolo, 'tipo': tipo,
                    'data_protocolo': data_protocolo, 'dias_espera': dias,
                    'delegacia': delegacia, 'estado': estado, 'cidade': cidade,
                    'servidor': servidor, 'relato': relato,
                    'anexos': anexos_string
                }
                
                df_reclamacoes = pd.concat([df_reclamacoes, pd.DataFrame([novo_registro])], ignore_index=True)
                save_data(df_reclamacoes)
                st.success(f"Protocolo registrado! {len(caminhos_arquivos)} arquivo(s) salvos com sucesso.")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")

with col2:
    st.markdown("### 📊 Estatísticas e Transparência")
    if not df_reclamacoes.empty:
        # Converter coluna de dias para numérico caso necessário
        df_reclamacoes['dias_espera'] = pd.to_numeric(df_reclamacoes['dias_espera'])
        
        df_grafico = df_reclamacoes.groupby('estado')['dias_espera'].mean().reset_index()
        fig = px.bar(df_grafico, x='estado', y='dias_espera', text_auto='.0f',
                     title="Média de Dias de Atraso por UF",
                     labels={'dias_espera': 'Média de Dias', 'estado': 'UF'},
                     color_discrete_sequence=['#2c3e50'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Histórico Recente")
        # Exibe apenas dados que não são sensíveis publicamente
        view_df = df_reclamacoes[['protocolo', 'tipo', 'estado', 'dias_espera']].tail(10)
        st.table(view_df)
    else:
        st.info("Nenhuma reclamação registrada até o momento.")
