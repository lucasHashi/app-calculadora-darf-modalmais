import pandas as pd
import streamlit as st

import calculadora_darf as calculos_darf


def main():
    st.title('Calculadora de DARF - Modelo da corretora Modal Mais')

    st.write('# Como é feito o calculo?')
    st.write('Essas são as minhas primeiras DARFs, então não sou o mais experiente nesse calculo')
    st.write('Segui esse tutorial pra fazer esse app:')
    st.write('https://www.youtube.com/watch?v=dZNy2BsHM90')

    st.write('# Calculadora de DARF')
    # arquivos_darf = calculos_darf.listar_arquivos_darf()
    # arquivos_darf.insert(0, 'Selecione um arquivo')
    # arquivos_darf.insert(0, 'Todos')

    # darf_escolhida = st.selectbox('', arquivos_darf)

    darf_escolhida = st.file_uploader('Carregue a nota de corretagem do mês', type='pdf')

    if darf_escolhida is not None:
        with st.spinner('Lendo o PDF e calculando o imposto...'):
            imposto_a_pagar = calculos_darf.calcular_imposto_a_pagar_darf(darf_escolhida)

            st.balloons()

        st.write('## Arquivo: {}'.format(darf_escolhida.name))
        st.write('# R$ {}'.format(imposto_a_pagar))


if __name__ == '__main__':
    main()
