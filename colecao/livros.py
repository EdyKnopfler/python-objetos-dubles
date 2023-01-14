import logging
from urllib.error import HTTPError
from urllib.request import urlopen
import os


def consultar_livros(autor):
    dados = preparar_dados_para_requisicao(autor)
    url = obter_url('http://buscador', dados)
    resultado = executar_requisicao(url)
    return resultado


def preparar_dados_para_requisicao(autor):
    pass


def obter_url(url, dados):
    pass


def executar_requisicao(url):
    with urlopen(url, timeout=10) as resposta:
        resultado = resposta.read().decode('utf-8')
    return resultado


def executar_requisicao_2(url):
    try:
        with urlopen(url, timeout=10) as resposta:
            resultado = resposta.read().decode('utf-8')
        return resultado
    except HTTPError as e:
        logging.exception(f'Erro de acesso ao acessar URL {url}: {str(e)}')
        return ''


def escrever_em_arquivo(arquivo, conteudo):
    diretorio = os.path.dirname(arquivo)

    try:
        os.makedirs(diretorio)
    except OSError:
        logging.exception(f'Não foi possível criar o diretório {diretorio}')

    try:
        with open(arquivo, 'w') as fp:
            fp.write(conteudo)
    except OSError:
        logging.exception(f'Não foi possível criar o arquivo {arquivo}')

