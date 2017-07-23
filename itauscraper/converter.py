"""Funções de conversão usada pelo scraper do Itaú."""
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from decimal import Decimal


def date(s):
    """Converte strings 'DD/MM' em datetime.date.
    Leva em consideração ano anterior para meses maiores que o mês corrente.
    """
    dt = parse(s, dayfirst=True)

    # Se o mês do lançamento > mês atual, o lançamento é do ano passado.
    if dt.month > datetime.date.today().month:
        dt += relativedelta(years=-1)

    return dt


def decimal(s):
    """Converte strings para Decimal('-9876.54').
    >>> assert decimal('9.876,54-') == Decimal('-9876.54')
    >>> assert decimal('9.876,54 D') == Decimal('-9876.54')
    >>> assert decimal('9.876,54 C') == Decimal('9876.54')
    >>> assert decimal('R$ 9.876,54') == Decimal('9876.54')
    >>> assert decimal('R$ -9.876,54') == Decimal('-9876.54')
    """
    s = s.replace('.', '')
    s = s.replace(',', '.')

    if s.startswith('R$ '):
        s = s[3:]

    if s.endswith('-'):
        s = s[-1] + s[:-1]
    elif s.endswith(' D'):
        s = '-' + s[:-2]
    elif s.endswith(' C'):
        s = s[:-2]

    return Decimal(s)


def is_balance(s):
    """Retorna True quando s é uma entrada de saldo em vez de lançamento."""
    return s in ('S A L D O',
                 '(-) SALDO A LIBERAR',
                 'SALDO FINAL DISPONIVEL',
                 'SALDO ANTERIOR')


def statements(iterable):
    """Converte dados do extrato de texto para tipos Python.
    Linhas de saldo são ignoradas.
    Entrada: (('21/07', 'Lançamento', '9.876,54-'), ...)
    Saída..: ((datetime.date(2017, 7, 21), 'Lançamento', Decimal('-9876.54')), ...)
    """
    return ((date(a), b, decimal(c)) for a, b, c in iterable if not is_balance(b))


def card_statements(iterable):
    """Converte dados do extrato do cartão de texto para tipos Python.
    Entrada: (('21/07', 'Lançamento', '9.876,54 D'), ...)
    Saída..: ((datetime.date(2017, 7, 21), 'Lançamento', Decimal('-9876.54')), ...)
    """
    return ((date(a), b, decimal(c)) for a, b, c in iterable)


def card_summary(iterable):
    """Converte dados do resumo do cartão de texto para tipos Python.
    Entrada: (('Item do Resumo', 'R$ -9.876,54'), ...)
    Saída..: (('Item do Resumo', Decimal('-9876.54')), ...)
    """
    return ((a, decimal(b)) for a, b in iterable)
