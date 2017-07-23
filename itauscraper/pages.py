"""Classes que sabem extrair conteúdos das páginas do Itaú."""
from lxml import html

from itauscraper.converter import card_statements, card_summary, statements
from itauscraper.itertools import grouper


class Page:
    """Classe base usada para extrair informações relevantes do Itaú."""

    def __init__(self, response):
        self.response = response
        self.tree = html.fromstring(response.content)

    def is_authenticated(self):
        return b"autenticado = 'S'" in self.response.content


class FirstPage(Page):
    """Página inicial de onde extrairemos a url de login válida."""

    def valid_login_url(self):
        # Extrai do html o parâmetro de sessão e anexa à url de login.
        url = 'https://ww70.itau.com.br/M/LoginPF.aspx'

        nl = self.tree.xpath("//a[starts-with(@href, '../Login')]/@href")
        href = nl[-1]
        param = href.split('?')[-1]
        url = ''.join((url, '?', param))
        return url


class LoginPage(Page):
    """Página de login de onde extraímos o formulário de autenticação."""

    def formdata(self, agencia, conta, digito, senha):
        # Extrai os nomes e valores dos campos do ASP.NET montando um dicionário.
        xpath = "//input[starts-with(@name, '__') and @value]/@*[name()='name' or name()='value']"
        viewstate = dict(grouper(self.tree.xpath(xpath)))

        # Prepara o dicionário com dados do post combinado os dados do ASP.NET e os dados da conta.
        data = {}
        data.update(viewstate)
        data.update({
            'ctl00$ContentPlaceHolder1$txtAgenciaT': agencia,
            'ctl00$ContentPlaceHolder1$txtContaT': conta,
            'ctl00$ContentPlaceHolder1$txtDACT': digito,
            'ctl00$ContentPlaceHolder1$txtPassT': senha,
            'ctl00$ContentPlaceHolder1$btnLogInT.x': '12',
            'ctl00$ContentPlaceHolder1$btnLogInT.y': '14',
            'ctl00$hddAppTokenApp': '',
            'ctl00$hddExisteApp': '',
        })

        return data


class MenuPage(Page):
    """Página com o menu de navegação do site do Itaú de onde extraímos as urls válidas."""

    def url_cartao(self):
        # Extrai do html a url das faturas do cartão.
        nl = self.tree.xpath("//span[.='CartÃµes']/ancestor::div[1]/a/@href")
        url = nl[-1]
        return url


class StatementPage(Page):
    def url_max_period(self):
        # Extrai do html o parâmetro da url para a listagem dos últimos 90 dias e anexa à url do extrato.
        url = 'https://ww70.itau.com.br/M/SaldoExtratoLancamentos.aspx'
        nl = self.tree.xpath("//a[starts-with(@href, 'Saldo')]/@href")
        href = nl[-1]
        param = href.split('?')[-1]
        url = ''.join((url, '?', param))
        return url

    def statements(self):
        # Extrai do html os lançamentos e transforma em
        xpath = "//fieldset[@id='ctl00_ContentPlaceHolder1_FieldExtratoTouch']//td[string-length(text())>1]/text()"
        nl = self.tree.xpath(xpath)
        data = tuple(grouper(nl, size=3))  # Reconstroi a tabela de 3 em 3.
        rows = data[1:]  # Ignora o cabeçalho da tabela.
        stmts = tuple(statements(rows))  # Converte textos para tipos Python
        return stmts


class CardMenuPage(Page):
    BASE_URL = 'https://ww70.itau.com.br/M/FaturaCartaoCreditoQT.aspx'

    def _url_menu(self, text):
        nl = self.tree.xpath("//div[.='LanÃ§amentos {}']/ancestor::div[1]/a/@href".format(text))
        href = nl[-1]
        param = href.split('?')[-1]
        url = ''.join((self.BASE_URL, '?', param))
        return url

    def url_menu_current(self):
        return self._url_menu('atuais')

    def url_menu_previous(self):
        return self._url_menu('anteriores')

    def url_menu_next(self):
        return self._url_menu('futuros')


class CardStatement(Page):
    def summary(self):
        xpath = "//table[@id='ctl00_ContentPlaceHolder1_tbResumoTableT']//td/text()"
        nl = self.tree.xpath(xpath)
        rows = tuple(grouper(nl, size=2))  # Reconstroi a tabela de 2 em 2.
        return dict(card_summary(rows))  # Converte textos para tipos Python

    def statements(self):
        # Extrai do html os lançamentos do cartão.
        xpath = "//table[@id='ctl00_ContentPlaceHolder1_tbmovnacionalT']//*[@class='saldo']//td/text()"
        nl = self.tree.xpath(xpath)
        data = tuple(grouper(nl, size=3))  # Reconstroi a tabela de 3 em 3.
        rows = data[1:]  # Ignora o lançamento de pagamento anterior.
        stmts = tuple(card_statements(rows))  # Converte textos para tipos Python
        return stmts
