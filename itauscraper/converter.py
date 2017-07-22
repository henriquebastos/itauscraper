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
    """Converte strings '9.876,54-' para Decimal('-9876.54')."""
    s = s.replace('.', '')
    s = s.replace(',', '.')

    if s.endswith('-'):
        s = s[-1] + s[:-1]

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
    Entrada: (('21/07/', 'Lançamento', '9.876,54-'), ...)
    Saída..: ((datetime.date(2017, 7, 21), 'Lançamento', Decimal('-9876.54')), ...)
    """
    return ((date(a), b, decimal(c)) for a, b, c in iterable if not is_balance(b))
