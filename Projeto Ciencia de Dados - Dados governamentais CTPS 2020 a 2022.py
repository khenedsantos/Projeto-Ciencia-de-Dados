#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

# Caminho para o arquivo CSV
csv_path = 'Dados_CTPS_2020-a-2022.csv'  # Certifique-se que o nome do arquivo esteja correto

# Tentar abrir o arquivo CSV com um encoding diferente (ISO-8859-1)
try:
    # Lendo o arquivo CSV com o encoding ISO-8859-1, que é compatível com caracteres especiais
    data = pd.read_csv(csv_path, encoding='ISO-8859-1', delimiter=';')
    print("Arquivo carregado com sucesso!")
    
    # Visualizar as 5 primeiras linhas do DataFrame
    print(data.head())
except FileNotFoundError:
    print(f"Erro: O arquivo '{csv_path}' não foi encontrado.")
except UnicodeDecodeError:
    print("Erro: Não foi possível decodificar o arquivo. Tente outro encoding.")
except Exception as e:
    print(f"Erro ao abrir o arquivo: {e}")


# In[2]:


import pandas as pd

# Caminho para o arquivo CSV (já carregado anteriormente)
csv_path = 'Dados_CTPS_2020-a-2022.csv'

# Carregar o CSV
data = pd.read_csv(csv_path, encoding='ISO-8859-1', delimiter=';')

# Nomes das colunas que são datas (ajuste os nomes conforme necessário)
colunas_de_data = ['Data Protocolo', 'Data CTPS', 'Data Emissão', 'Data Nascimento']

# Converter as colunas de data para o formato datetime
for coluna in colunas_de_data:
    if coluna in data.columns:
        data[coluna] = pd.to_datetime(data[coluna], errors='coerce', format='%d/%m/%Y')

# Verificar as conversões
print(data.dtypes)  # Exibir os tipos das colunas para verificar se foram convertidas
print(data.head())  # Exibir as primeiras linhas para conferir as datas

# Mostrar as primeiras linhas para garantir que as datas estão no formato correto


# In[3]:


import pandas as pd

# Caminho para o arquivo CSV (já carregado anteriormente)
csv_path = 'Dados_CTPS_2020-a-2022.csv'

# Carregar o CSV
data = pd.read_csv(csv_path, encoding='ISO-8859-1', delimiter=';')

# Nomes das colunas que são datas (ajuste os nomes conforme necessário)
colunas_de_data = ['Data Protocolo', 'Data CTPS', 'Data Emissão', 'Data Nascimento']

# Converter as colunas de data para o formato datetime sem especificar o formato exato
for coluna in colunas_de_data:
    if coluna in data.columns:
        data[coluna] = pd.to_datetime(data[coluna], errors='coerce')

# Verificar as conversões
print(data.dtypes)  # Exibir os tipos das colunas para verificar se foram convertidas
print(data.head())  # Exibir as primeiras linhas para conferir as datas

# Mostrar resumo das colunas de data para identificar a quantidade de valores NaT
for coluna in colunas_de_data:
    if coluna in data.columns:
        print(f"\nResumo da coluna {coluna}:")
        print(data[coluna].describe(datetime_is_numeric=True))


# In[4]:


# Verificar os primeiros valores das colunas de data para entender possíveis problemas
colunas_de_data = ['Data Protocolo', 'Data CTPS', 'Data Emissão', 'Data Nascimento']

for coluna in colunas_de_data:
    if coluna in data.columns:
        print(f"\nValores na coluna {coluna}:")
        print(data[coluna].dropna().unique()[:10])  # Mostrar os primeiros 10 valores não nulos da coluna


# In[5]:


# Verificar os primeiros valores das colunas de data sem aplicar qualquer conversão
for coluna in colunas_de_data:
    if coluna in data.columns:
        print(f"\nPrimeiros valores da coluna {coluna}:")
        print(data[coluna].head(10))  # Mostrar os primeiros 10 valores da coluna original


# In[6]:


# Verificar os tipos e valores originais das colunas de data
for coluna in colunas_de_data:
    if coluna in data.columns:
        print(f"\nColuna {coluna} - Tipo Original: {data[coluna].dtype}")
        print(data[coluna].head(10))  # Mostrar os primeiros 10 valores da coluna para entender melhor o formato original


# In[7]:


# Carregar o CSV novamente, sem tentar converter qualquer coluna
data_raw = pd.read_csv(csv_path, encoding='ISO-8859-1', delimiter=';')

# Verificar os primeiros valores das colunas de data no arquivo bruto
for coluna in colunas_de_data:
    if coluna in data_raw.columns:
        print(f"\nPrimeiros valores da coluna {coluna} no arquivo original:")
        print(data_raw[coluna].head(10))  # Mostrar os primeiros 10 valores do arquivo bruto


# In[8]:


import pandas as pd

# Caminho para o arquivo CSV (carregar novamente o arquivo bruto)
data_raw = pd.read_csv(csv_path, encoding='ISO-8859-1', delimiter=';')

# Função para tentar converter os valores numéricos grandes em datas
def converter_para_data(valor):
    try:
        # Converter o valor para string e pegar apenas os primeiros dígitos que parecem uma data
        valor_str = str(int(valor))  # Converter o valor para inteiro e depois para string
        if len(valor_str) >= 8:
            # Considerando que os 8 primeiros dígitos representam algo como AAAAMMDD
            ano = valor_str[:4]
            mes = valor_str[4:6]
            dia = valor_str[6:8]
            return f"{ano}-{mes}-{dia}"
        else:
            return pd.NaT
    except:
        return pd.NaT

# Aplicar a função de conversão às colunas de data
colunas_de_data = ['Data Protocolo', 'Data Emissão', 'Data Nascimento']
for coluna in colunas_de_data:
    if coluna in data_raw.columns:
        data_raw[coluna] = data_raw[coluna].apply(converter_para_data)

# Converter as colunas para o formato datetime
for coluna in colunas_de_data:
    if coluna in data_raw.columns:
        data_raw[coluna] = pd.to_datetime(data_raw[coluna], errors='coerce')

# Verificar o resultado
print(data_raw.dtypes)  # Verificar os tipos de dados das colunas
print(data_raw.head())  # Mostrar as primeiras linhas do DataFrame para verificar as datas


# In[9]:


# Verificar os primeiros valores e as suas características
for coluna in colunas_de_data:
    if coluna in data_raw.columns:
        print(f"\nColuna: {coluna}")
        print(f"Primeiros valores brutos:")
        print(data_raw[coluna].head(10))  # Mostrar os primeiros 10 valores

        # Identificar se os valores podem ser numéricos e verificar o tipo
        print(f"Tipos de valores:")
        print(data_raw[coluna].apply(lambda x: type(x)).unique())


# In[10]:


# Verificar a quantidade de valores não nulos nas colunas de data
for coluna in colunas_de_data:
    if coluna in data_raw.columns:
        print(f"\nQuantidade de valores não nulos na coluna {coluna}: {data_raw[coluna].notna().sum()}")


# In[11]:


# Remover as colunas de data que estão vazias
data_limpo = data_raw.drop(columns=colunas_de_data)

# Verificar a estrutura do DataFrame após a remoção das colunas
print(data_limpo.info())

# Mostrar as primeiras linhas do DataFrame
print(data_limpo.head())


# In[12]:


# Importar as bibliotecas necessárias
import pandas as pd

# Explorar a distribuição dos valores nas colunas categóricas
for coluna in data_limpo.columns:
    print(f"\nDistribuição da coluna: {coluna}")
    print(data_limpo[coluna].value_counts())

# Verificar se há valores duplicados
duplicados = data_limpo.duplicated().sum()
print(f"\nNúmero de registros duplicados: {duplicados}")

# Resumo estatístico das colunas numéricas, se houver
print("\nResumo estatístico das colunas numéricas:")
print(data_limpo.describe())


# In[12]:


# Remover colunas que possuem apenas valores nulos
colunas_vazias = data_limpo.columns[data_limpo.isna().all()]
data_limpo = data_limpo.drop(columns=colunas_vazias)

# Verificar se as colunas foram removidas
print(f"Colunas removidas: {colunas_vazias}")


# In[13]:


# Mostrar as colunas restantes no DataFrame
print("Colunas restantes no DataFrame:")
print(data_limpo.columns)

# Mostrar as 5 primeiras linhas do DataFrame
print("\nPrimeiras 5 linhas do DataFrame:")
print(data_limpo.head())

# Mostrar as 5 últimas linhas do DataFrame
print("\nÚltimas 5 linhas do DataFrame:")
print(data_limpo.tail())

# Definir o caminho para salvar o arquivo CSV
caminho_csv = r"C:\temp\Dados_CTPS_Tratados.csv"

# Salvar o DataFrame em um arquivo CSV
try:
    data_limpo.to_csv(caminho_csv, index=False, encoding='utf-8')
    print(f"\nArquivo salvo com sucesso em: {caminho_csv}")
except Exception as e:
    print(f"Erro ao salvar o arquivo: {e}")


# In[15]:


linhas, colunas = data_limpo.shape
print(f"O DataFrame possui {linhas} linhas e {colunas} colunas.")


# In[16]:


# Verificar se ainda há registros duplicados
duplicados_restantes = data_limpo.duplicated().sum()

print(f"Número de registros duplicados restantes: {duplicados_restantes}")


# In[17]:


# Remover registros duplicados do DataFrame
data_limpo_sem_duplicados = data_limpo.drop_duplicates()

# Verificar se foram removidos os registros duplicados
duplicados_restantes = data_limpo_sem_duplicados.duplicated().sum()
print(f"Número de registros duplicados restantes após remoção: {duplicados_restantes}")


# In[18]:


# Remover registros duplicados
data_limpo_sem_duplicados = data_limpo.drop_duplicates()

# Definir caminho para salvar o arquivo na pasta temp
caminho_csv = r'C:\temp\Dados_CTPS_Tratados_Sem_Duplicados.csv'

# Salvar o DataFrame limpo em um arquivo CSV
try:
    data_limpo_sem_duplicados.to_csv(caminho_csv, index=False, encoding='utf-8')
    print(f"Arquivo salvo com sucesso em: {caminho_csv}")
except Exception as e:
    print(f"Erro ao salvar o arquivo: {e}")


# In[ ]:




