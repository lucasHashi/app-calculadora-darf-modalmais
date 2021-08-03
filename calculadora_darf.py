import pandas as pd
import numpy as np
import tabula

import os
import pathlib
import uuid

import warnings
warnings.filterwarnings("ignore")





def main():
    arquivos_darf = listar_arquivos_darf()

    darf_escolhida = arquivos_darf[0]

    imposto_a_pagar = calcular_imposto_a_pagar_darf(darf_escolhida)

    print(darf_escolhida)
    print('R$', imposto_a_pagar)




def listar_arquivos_darf():
    return list(os.listdir(os.path.join('.', 'darfs')))


def carregar_darf(arquivo):
    dfs_darf = []

    indice_pagina = 1
    pagina_valida = True
    while pagina_valida:
        try:
            df_darf = tabula.read_pdf(
                arquivo,
                pages = indice_pagina
            )

            dfs_darf.append(df_darf)
            indice_pagina += 1
        except tabula.io.subprocess.CalledProcessError:
            pagina_valida = False

    return dfs_darf


def carregar_darf_por_caminho(nome_arquivo):
    dfs_darf = []

    indice_pagina = 1
    pagina_valida = True
    while pagina_valida:
        try:
            df_darf = tabula.read_pdf(
                os.path.join('.', 'darfs', nome_arquivo),
                pages = indice_pagina
            )

            dfs_darf.append(df_darf)
            indice_pagina += 1
        except tabula.io.subprocess.CalledProcessError:
            pagina_valida = False

    return dfs_darf


def carregar_darf_por_arquivo(arquivo):
    dfs_darf = []

    indice_pagina = 1
    pagina_valida = True
    # Passa pagina-a-pagina ate que de erro pois as paginas acabaram
    while pagina_valida:

        # Solucao para o problema de PDFs entre Streamlit e Tabula
        #   Tabula so aceita o caminho do arquivo
        #   Streamlit retorna um fdsafdas
        # Solucao em: https://discuss.streamlit.io/t/how-to-upload-a-pdf-file-in-streamlit/2428/7
        # Salva o PDF em um caminho temporario, le o que precisa e depois apaga.
        try:
            fp = pathlib.Path(str(uuid.uuid4())) # Cria caminho temp
            try:
                fp.write_bytes(arquivo.getvalue()) # Salva o PDF

                # Trabalha com o PDF antes de ser apagado
                df_darf = tabula.read_pdf(
                    fp,
                    pages = indice_pagina
                )

                dfs_darf.append(df_darf)
                indice_pagina += 1
            finally:
                # Apaga o arquivo
                if fp.is_file():
                    fp.unlink()
        except tabula.io.subprocess.CalledProcessError: # Erro ao chegar no final do PDF
            pagina_valida = False

    return dfs_darf


def carregar_valores_darf(arquivo_darf):
    try:
        dfs_darf_escolhida = carregar_darf(arquivo_darf)
    except ValueError:
        dfs_darf_escolhida = carregar_darf_por_arquivo(arquivo_darf)
    except Exception:
        dfs_darf_escolhida = carregar_darf_por_caminho(arquivo_darf)

    dados_completos_darf = []
    for pagina in dfs_darf_escolhida:
        dados_pagina = {}

        pagina = [df for df in pagina if not df.empty]

        df_cabecalho = pagina[0]
        # Dados do cabecalho
        dados_pagina['num_nota'] = df_cabecalho.iloc[1, 2]
        dados_pagina['data_pregao'] = df_cabecalho.iloc[1, 4]

        df_rodape = pagina[1]
        # Dados do rodape
        #   Taxas e impostos
        dados_pagina['irrf_day_trade'] = df_rodape.iloc[2, 4]
        dados_pagina['taxa_operacional'] = df_rodape.iloc[2, 5]
        dados_pagina['taxa_registro_bmf'] = df_rodape.iloc[2, 6]
        dados_pagina['taxa_bmf'] = df_rodape.iloc[2, -1]
        #   Valores descontados
        dados_pagina['total_conta_normal'] = df_rodape.iloc[7, 5]
        dados_pagina['total_liquido'] = df_rodape.iloc[7, 6]

        dados_completos_darf.append(dados_pagina)
    
    df_dados_darf = pd.DataFrame(dados_completos_darf)

    df_dados_darf.drop_duplicates(subset=['data_pregao'])

    df_dados_darf['data_pregao'] = pd.to_datetime(df_dados_darf['data_pregao'], format='%d/%m/%Y')

    df_dados_darf['irrf_day_trade'] = pd.to_numeric(df_dados_darf['irrf_day_trade'].str.replace('.', '').str.replace(',', '.'))

    df_dados_darf['taxa_operacional'] = pd.to_numeric(df_dados_darf['taxa_operacional'].str.replace('.', '').str.replace(',', '.'))
    df_dados_darf['taxa_registro_bmf'] = pd.to_numeric(df_dados_darf['taxa_registro_bmf'].str.replace('.', '').str.replace(',', '.'))
    df_dados_darf['taxa_bmf'] = pd.to_numeric(df_dados_darf['taxa_bmf'].str.replace(' \| D', '').str.replace(' \| C', '').str.replace('.', '').str.replace(',', '.'))

    df_dados_darf['total_liquido'] = df_dados_darf['total_liquido'].str.replace(' \| D', '').str.replace(' \| C', '')
    df_dados_darf[['total_conta_normal', 'direcao_resultado']] = df_dados_darf['total_conta_normal'].str.split(' \| ', expand=True)

    df_dados_darf['total_liquido'] = pd.to_numeric(df_dados_darf['total_liquido'].str.replace('.', '').str.replace(',', '.'))
    df_dados_darf['total_conta_normal'] = pd.to_numeric(df_dados_darf['total_conta_normal'].str.replace('.', '').str.replace(',', '.'))

    df_dados_darf.loc[df_dados_darf['direcao_resultado'] == 'D', 'total_conta_normal'] = df_dados_darf.loc[df_dados_darf['direcao_resultado'] == 'D', 'total_conta_normal'] * -1

    return df_dados_darf


def calcular_imposto_a_pagar_darf(arquivo_darf):
    df_resultados_darf = carregar_valores_darf(arquivo_darf)

    soma_conta_normal = df_resultados_darf['total_conta_normal'].sum()
    soma_irrf = df_resultados_darf['irrf_day_trade'].sum()

    imposto_a_pagar = soma_conta_normal - soma_irrf
    imposto_a_pagar = imposto_a_pagar * 0.19
    imposto_a_pagar = np.ceil(imposto_a_pagar * 100) / 100

    return imposto_a_pagar








if __name__ == '__main__':
    main()