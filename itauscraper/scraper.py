"""Lógica do navegação no site do Itaú."""
import requests

from itauscraper.pages import CardMenuPage, StatementPage, MenuPage, LoginPage, FirstPage, CardStatement


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
        response = self.session.get(url)
        page = FirstPage(response)

        url = page.valid_login_url()

        # Faz um GET na url válida de login para exibir o formulário com campos do ASP.NET.
        response = self.session.get(url)
        page = LoginPage(response)

        # Faz o POST realizando o login.
        data = page.formdata(self.agencia, self.conta, self.digito, self.senha)
        response = self.session.post(url, data=data)
        page = MenuPage(response)

        return page

    def extrato(self):
        url = 'https://ww70.itau.com.br/M/SaldoExtratoLancamentos.aspx'

        # Assumindo que estamos logados, faz um GET na url que lista os lançamentos.
        # Por padrão serão mostrados lançamentos realizados nos últimos 3 dias.
        response = self.session.get(url)
        page = StatementPage(response)

        url = page.url_max_period()

        # Faz um GET para listar os lançamentos dos últimos 90 dias, que é o maior período possível.
        response = self.session.get(url)
        page = StatementPage(response)

        stmts = page.statements()

        return stmts

    def cartao(self):
        url = 'https://ww70.itau.com.br/M/FaturaCartaoCreditoQT.aspx'

        # Assumindo que estamos logados, faz um GET na url que lista o menu do cartão.
        response = self.session.get(url)
        page = CardMenuPage(response)

        # Faz um GET para listar os lançåmentos atuais do cartão.
        url = page.url_menu_current()
        response = self.session.get(url)
        page = CardStatement(response)

        summary = page.summary()
        stmts = page.statements()

        return summary, stmts

