"""Lógica do navegação no site do Itaú."""
from lxml import html
import requests

from itauscraper.converter import statements
from itauscraper.itertools import grouper


class MobileSession(requests.Session):
    """Session customizado para se passar por navegador de dispositivo móvel."""

    def __init__(self):
        super().__init__()

        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
            'Accept': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4',
        })


class ItauScraper:
    """Scraper do Itaú Pessoa Física."""

    def __init__(self, agencia, conta, digito, senha):
        self.agencia = agencia
        self.conta = conta
        self.digito = digito
        self.senha = senha

        self.session = MobileSession()

    def login(self):
        url = 'https://ww70.itau.com.br/M/LoginPF.aspx'

        # Faz um GET na url inválida de login para descobrir o parâmetro de sessão.
        page = self.session.get(url)
        tree = html.fromstring(page.content)

        # Extrai do html o parâmetro de sessão e anexa à url de login.
        nl = tree.xpath("//a[starts-with(@href, '../Login')]/@href")
        href = nl[-1]
        param = href.split('?')[-1]
        url = ''.join((url, '?', param))

        # Faz um GET na url válida de login para exibir o formulário com campos do ASP.NET.
        page = self.session.get(url)
        tree = html.fromstring(page.content)

        # Extrai os nomes e valores dos campos do ASP.NET montando um dicionário.
        xpath = "//input[starts-with(@name, '__') and @value]/@*[name()='name' or name()='value']"
        viewstate = dict(grouper(tree.xpath(xpath)))

        # Prepara o dicionário com dados do post combinado os dados do ASP.NET e os dados da conta.
        data = {}
        data.update(viewstate)
        data.update({
            'ctl00$ContentPlaceHolder1$txtAgenciaT': self.agencia,
            'ctl00$ContentPlaceHolder1$txtContaT': self.conta,
            'ctl00$ContentPlaceHolder1$txtDACT': self.digito,
            'ctl00$ContentPlaceHolder1$txtPassT': self.senha,
            'ctl00$ContentPlaceHolder1$btnLogInT.x': '12',
            'ctl00$ContentPlaceHolder1$btnLogInT.y': '14',
            'ctl00$hddAppTokenApp': '',
            'ctl00$hddExisteApp': '',
        })

        # Faz o POST realizando o login.
        page = self.session.post(url, data=data)

        # Verifica se o login foi bem sucedido checando uma dica no javascript gerado pela página.
        authenticaded = b"autenticado = 'S'" in page.content

        # Retorna True ou False de acordo com o resultado do login.
        return authenticaded

    def extrato(self):
        url = 'https://ww70.itau.com.br/M/SaldoExtratoLancamentos.aspx'

        # Assumindo que estamos logados, faz um GET na url que lista os lançamentos.
        # Por padrão serão mostrados lançamentos realizados nos últimos 3 dias.
        page = self.session.get(url)
        tree = html.fromstring(page.content)

        # Extrai do html o parâmetro da url para a listagem dos últimos 90 dias e anexa à url do extrato.
        nl = tree.xpath("//a[starts-with(@href, 'Saldo')]/@href")
        href = nl[-1]
        param = href.split('?')[-1]
        url = ''.join((url, '?', param))

        # Faz um GET para listar os lançamentos dos últimos 90 dias, que é o maior período possível.
        page = self.session.get(url)
        tree = html.fromstring(page.content)

        # Extrai do html os lançamentos e transforma em
        xpath = "//fieldset[@id='ctl00_ContentPlaceHolder1_FieldExtratoTouch']//td[string-length(text())>1]/text()"
        nl = tree.xpath(xpath)
        data = tuple(grouper(nl, size=3))  # Reconstroi a tabela de 3 em 3.
        rows = data[1:]                    # Ignora o cabeçalho da tabela.
        stmts = tuple(statements(rows))    # Converte textos para tipos Python

        return stmts
