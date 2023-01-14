from unittest.mock import patch, mock_open, Mock, MagicMock
#from unittest import skip
from urllib.error import HTTPError

import pytest

from colecao.livros import (
    consultar_livros,
    executar_requisicao,
    executar_requisicao_2,
    escrever_em_arquivo
)


# stub: fornece um dado pré-fabricado indiretamente ligado aos testes
class StubHttpResponse:
    def read(self):
        return b''

    def __enter__(self):  # open
        return self

    def __exit__(self, param1, param2, param3):  # close
        pass


def stub_de_urlopen(url, timeout):
    return StubHttpResponse()


#@skip('testaremos quando executar_requisicao estiver implementado')
@patch('colecao.livros.urlopen', return_value=StubHttpResponse())
def test_consultar_livros_retorna_resultado_formato_string(stub_urlopen):
    resultado = consultar_livros('Agatha Christie')
    assert type(resultado) == str


@patch('colecao.livros.urlopen', return_value=StubHttpResponse())
def test_consultar_livros_chama_preparar_dados_para_requisicao_uma_vez_com_os_mesmos_parametros_recebidos(
        stub_urlopen):
    # spy: verifica os parâmetros da chamada
    with patch('colecao.livros.preparar_dados_para_requisicao') as spy_preparar_dados:
        consultar_livros('Agatha Christie')
        spy_preparar_dados.assert_called_once_with('Agatha Christie')


@patch('colecao.livros.urlopen', return_value=StubHttpResponse())
def test_consultar_livros_chama_obter_url_usando_como_parametro_o_retorno_de_preparar_dados_para_requisicao(
        stub_urlopen):
    # ainda não nos preocupamos em completar preparar_dados_para_requisicao
    with patch('colecao.livros.preparar_dados_para_requisicao') as stub_preparar:
        dados = {'autor': 'Agatha Christie'}
        stub_preparar.return_value = dados
        # o que a consultar_livros deve fazer: pegar o retorno de preparar_... e passar para obter_url
        with patch('colecao.livros.obter_url') as spy_obter_url:
            consultar_livros('Agatha Christie')
            spy_obter_url.assert_called_once_with('http://buscador', dados)


@patch('colecao.livros.urlopen', return_value=StubHttpResponse())
def test_consultar_livros_chama_executar_requisicao_usando_retorno_de_obter_url(stub_urlopen):
    with patch('colecao.livros.obter_url') as stub_obter_url:
        stub_obter_url.return_value = 'exemplo de URL'
        with patch('colecao.livros.executar_requisicao') as spy_executar_requisicao:
            consultar_livros('Agatha Christie')
            spy_executar_requisicao.assert_called_once_with('exemplo de URL')


def test_consultar_livros_retorna_o_retorno_de_executar_requisicao():
    with patch('colecao.livros.executar_requisicao') as duble:  # este dublê é um mock?
        duble.return_value = 'kkk'
        ret = consultar_livros('Agatha Christie')
        assert ret == 'kkk'


# testando com stub
def test_executar_requisicao_retorna_string_stub():
    # patch na variável do módulo criada pelo import
    # eu mesmo especifico a função substituindo
    with patch('colecao.livros.urlopen', stub_de_urlopen):
        resultado = executar_requisicao('url_buscar_livros')
        assert type(resultado) == str


# testando com mock
def test_executar_requisicao_retorna_string_mock():
    # o patch cria um objeto Mock
    with patch('colecao.livros.urlopen') as mock_de_urlopen:
        mock_de_urlopen.return_value = StubHttpResponse()
        resultado = executar_requisicao('url_buscar_livros')
        assert type(resultado) == str


def test_executar_requisicao_retorna_string_mock_2():
    # mais conciso
    with patch('colecao.livros.urlopen', return_value=StubHttpResponse()):
        resultado = executar_requisicao('url_buscar_livros')
        assert type(resultado) == str


# com decorador
@patch('colecao.livros.urlopen', return_value=StubHttpResponse())
def test_executar_requisicao_retorna_string_mock_3(duble_urlopen):  # recebe como parâmetro
    resultado = executar_requisicao('url_buscar_livros')
    assert type(resultado) == str


# com decorador 2
@patch('colecao.livros.urlopen')
def test_executar_requisicao_retorna_string_mock_3(duble_urlopen):  # recebe como parâmetro
    duble_urlopen.return_value = StubHttpResponse()
    resultado = executar_requisicao('url_buscar_livros')
    assert type(resultado) == str


def test_executar_requisicao_levanta_excecao_do_tipo_http_error_1():
    with patch('colecao.livros.urlopen', stub_que_lanca_erro):
        with pytest.raises(HTTPError) as excecao:
            executar_requisicao('urlkkkkkk')
        assert 'msg de erro' in str(excecao.value)


class Dummy:
    pass


def stub_que_lanca_erro(url, timeout):
    fp = mock_open  # gerenciador de contexto (with)
    fp.close = Dummy
    raise HTTPError(Dummy(), Dummy(), 'msg de erro', Dummy(), fp)


@patch('colecao.livros.urlopen')
def test_executar_requisicao_levanta_excecao_do_tipo_http_error_2(duble_urlopen):
    fp = mock_open
    fp.close = Mock()
    # ensinando o mock a lançar exceção
    duble_urlopen.side_effect = HTTPError(Mock(), Mock(), 'msg de erro', Mock(), fp)
    with pytest.raises(HTTPError) as excecao:
        executar_requisicao('iti malia')
    assert 'msg de erro' in str(excecao.value)


# imaginando uma versão alternativa da executar_requisicao que não lança, e sim trata a exceção

# caplog = fixture do pytest!
def test_executar_requisicao_2_loga_mensagem_de_erro_de_http_error_1(caplog):
    with patch('colecao.livros.urlopen', stub_que_lanca_erro):
        executar_requisicao_2('mimimimi')
        assert len(caplog.records) == 1
        for registro in caplog.records:
            assert 'Erro de acesso' in registro.message


def duble_os_makedirs(diretorio):
    raise OSError('S.O. de folga, nenhum diretório criado')


class DubleLogging:

    def __init__(self):
        self._mensagens = []

    def exception(self, msg):
        self._mensagens.append(msg)

    @property
    def mensagens(self):
        return self._mensagens


def test_escrever_em_arquivo_registra_excecao_que_nao_foi_possivel_criar_diretorio():
    arquivo = '/tmp/arquivo'
    conteudo = 'severina xique xique'
    with patch('colecao.livros.os.makedirs', duble_os_makedirs):
        duble_logging = DubleLogging()
        with patch('colecao.livros.logging', duble_logging):
            escrever_em_arquivo(arquivo, conteudo)
            assert 'Não foi possível criar o diretório /tmp' in duble_logging.mensagens


# atenção para a ordem dos patches e dos parâmetros :P
@patch('colecao.livros.os.makedirs')
@patch('colecao.livros.logging.exception')
@patch('colecao.livros.open', side_effect=OSError())
def test_escrever_em_arquivo_registra_erro_ao_criar_arquivo(stub_open, spy_logging_exception, stub_os_makedirs):
    arq = './mimimi/buaaa.json'
    escrever_em_arquivo(arq, 'xoro')
    spy_logging_exception.assert_called_once_with(f'Não foi possível criar o arquivo {arq}')


# criando spy de gerenciador de contexto "na unha"
class SpyFp:

    def __init__(self):
        self._conteudo = None

    def __enter__(self):
        return self

    def __exit__(self, p1, p2, p3):
        pass

    def write(self, conteudo):
        self._conteudo = conteudo


@patch('colecao.livros.os.makedirs')
@patch('colecao.livros.open')
def test_escrever_em_arquivo_chama_write_1(stub_open, stub_os_makedirs):
    spy_fp = SpyFp()
    stub_open.return_value = spy_fp
    escrever_em_arquivo('/pastinha/arquivim', 'nada')
    assert spy_fp._conteudo == 'nada'


# usando MagicMock
@patch('colecao.livros.os.makedirs')
@patch('colecao.livros.open')
def test_escrever_em_arquivo_chama_write_2(stub_open, stub_os_makedirs):
    spy_fp = MagicMock()
    spy_fp.__enter__.return_value = spy_fp  # esse cara que devolve o fp, usamos o mesmo objeto
    stub_open.return_value = spy_fp
    escrever_em_arquivo('/pastinha/arquivim', 'nada')
    spy_fp.write.assert_called_once_with('nada')
