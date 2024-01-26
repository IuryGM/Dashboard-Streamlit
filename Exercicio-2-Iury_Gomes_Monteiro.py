import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def gerar_dataframe_final():
    df_IBYTE=pd.read_csv('RECLAMEAQUI_IBYTE.csv')
    df_HAPVIDA=pd.read_csv('RECLAMEAQUI_HAPVIDA.csv')
    df_NAGEM=pd.read_csv('RECLAMEAQUI_NAGEM.csv')

    df_IBYTE['EMPRESA'] = 'IBYTE'
    df_HAPVIDA['EMPRESA'] = 'HAPVIDA'
    df_NAGEM['EMPRESA'] = 'NAGEM'

    df = pd.concat([df_IBYTE, df_HAPVIDA, df_NAGEM]).reset_index(drop=True)

    df['TEMPO']=pd.to_datetime(df['TEMPO'], utc=False)
    municipio_rows = []
    estado_rows = []
    
    for i, row in df.iterrows():
        [municipio, estado] = row['LOCAL'].split(' - ')
        municipio_rows.append(municipio)
        estado_rows.append(estado)
        
    df['MUNICIPIO'] = municipio_rows
    df['ESTADO'] = estado_rows
    df['TAMANHO_DESCRICAO'] = df['DESCRICAO'].str.len()
    df = df.drop(['LOCAL'], axis=1)
    
    df = df.loc[~((df['ESTADO'] == '--') | (df['ESTADO'] == 'naoconsta') | (df['ESTADO'] == '') | (df['ESTADO'] == 'P') | (df['ESTADO'] == 'C'))]

    return df

def gerar_checkbox_status(features):
    st.session_state.columns = features

    for coluna in features:
        st.session_state[coluna] = True
    
def gerar_status_list(status_list):
    status_list = np.insert(status_list, 0, 'Todos')    
    return status_list

def gerar_opcoes_selecao_estado(estados_list):
    return np.insert(estados_list, 0, 'Todos')

def main():    
    df = gerar_dataframe_final()
    
    empresas = df['EMPRESA'].unique()
    features = df.columns
    
    gerar_checkbox_status(features)
        
    status_list = gerar_status_list(pd.unique(df['STATUS'])) 
    
    estados_list = gerar_opcoes_selecao_estado(pd.unique(df['ESTADO']))
    
    st.set_page_config(
        page_title = "Reclame Aqui Dashboard",
        layout="wide"
    )

    st.session_state.total_experimentos = len(df)
    
    data = None
    
    with st.sidebar:
        empresas_selected = st.multiselect(
            label="Selecione a Empresa", options=empresas, default=empresas
        )

        status_filter = st.selectbox("Selecione o Status", status_list)
        
        estado_filter = st.selectbox('Selecione o Estado', estados_list)
                                                                
        included = st.expander('Seleção de Features', expanded=False)
        
        with included:
            st.write('')

        for col in features:
            with included:
                st.session_state[col] = st.checkbox(col, value=True)  
                
    if not empresas_selected:
        data = df
    else:
        data = df[df['EMPRESA'].isin(empresas_selected)]
        
    if status_filter != 'Todos':
        data = data[data["STATUS"] == status_filter]        

    if estado_filter != 'Todos':
        data = data[data['ESTADO'] == estado_filter]

    tamanho_max_texto = data['DESCRICAO'].str.len().max()
    
    with st.sidebar:
        numero_caracteres = st.slider('Número de caracteres', 1, 
                                value = tamanho_max_texto,
                                max_value = tamanho_max_texto)

        data = data[data['DESCRICAO'].str.len() <= numero_caracteres]

    numero_linhas = st.slider('Número de Reclamações', 1, 
                                value = len(data),
                                max_value = len(data))

    data = data.reset_index()

    data = data.iloc[0:numero_linhas]
    
    columns_selected = []
    
    for col in features:
        if st.session_state[col]:
            columns_selected.append(col)
    if len(columns_selected) == 0:
        columns_selected = features        
    
    data = data[columns_selected]

    tab_dados, tab_temporal_series, tab_freq_reclamacao, tab_freq_status, tab_size_descricao = st.tabs(["Dados Gerais", "Series Temporais", "Frequência Reclamações", "Frequência Status", "Tamanho Descrição"])

    with tab_dados:        
        st.write("### Dados do Reclame Aqui", data.sort_index())
        
    with tab_temporal_series:
        st.line_chart(data, x="TEMPO", y="CASOS")
        
    with tab_freq_reclamacao:
        st.bar_chart(data, x="ESTADO", y="CASOS")
        
    with tab_freq_status:
        st.bar_chart(data, x="STATUS", y="CASOS")
        
    with tab_size_descricao:
        st.bar_chart(data, x="STATUS", y="TAMANHO_DESCRICAO")
        st.bar_chart(data, x="ESTADO", y="TAMANHO_DESCRICAO")
        st.bar_chart(data, x="EMPRESA", y="TAMANHO_DESCRICAO")
    
    


main()