import streamlit as st
from backend.main import get_all_data
import pandas as pd
import json

with open('./data/db.json', 'r') as data:
    tabelas = json.load(data)

# Função para adicionar uma nova tabela
def adicionar_tabela(nome, endereco, intervalo, path):
    dados =  get_all_data(endereco, intervalo, path)[0]
    dados = [d.model_dump() for d in dados]
    tabelas[nome] = {
        'nome': nome,
        'endereco': endereco,
        'intervalo': intervalo,
        'path': path,
        'dados': dados
    }
    print(tabelas[nome])

# Função para criar abas dinamicamente
def criar_abas():
    nomes_tabelas = list(tabelas.keys())
    opcao = st.sidebar.radio("Escolha uma tabela:", nomes_tabelas)
    return opcao

# Função para emitir uma tabela com cores
def emitir_tabela_com_cores(tabela):
    st.header(f"Tabela: {tabela['nome']}")
    dados = tabela['Cte_Data']
    df = pd.DataFrame(dados)

    st.dataframe(df)
    for i, item in enumerate(dados):
        cor_de_fundo = 'red' if item['valor_frete'] > 100 else 'green'
        st.markdown(f'<style>.row:nth-child({i + 2}) > div {{background-color: {cor_de_fundo};}}</style>', unsafe_allow_html=True)

# Aplicativo Streamlit
st.title("Aplicativo CRUD de Tabelas")

# Botão para adicionar uma nova tabela
if st.button("Adicionar Tabela"):
    with st.form(key="nova_tabela_form"):
        nome = st.text_input("Nome da Tabela")
        endereco = st.text_input("Endereço")
        intervalo = st.text_input("Intervalo")
        path = st.text_input("Caminho para salvar a tabela (ex: tabela.csv)")
        if st.form_submit_button("Criar Tabela"):
            print("Tabela")
            adicionar_tabela(nome, endereco, intervalo, path)

# Lista de abas para cada tabela
opcao = criar_abas()
if opcao:
    tabela = tabelas[opcao]
    emitir_tabela_com_cores(tabela)

# Função que pega os dados da tabela

# Exemplo de uso da função para obter dados e atualizar a tabela "Tabela1"
if st.button("Atualizar Tabela"):
    pass