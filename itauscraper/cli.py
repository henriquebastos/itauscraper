"""Command line interface."""
import argparse

from tabulate import tabulate

from itauscraper.scraper import ItauScraper


def main():
    parser = argparse.ArgumentParser(prog='itau',
                                     description='Scraper para baixar seus extratos do Itaú com um comando.')

    parser.add_argument('--agencia', '-a', help='Agência na forma 0000', required=True)
    parser.add_argument('--conta', '-c', help='Conta sem dígito na forma 00000', required=True)
    parser.add_argument('--digito', '-d', help='Dígito da conta na forma 0', required=True)
    parser.add_argument('--senha', '-s', help='Senha eletrônica da conta no Itaú.', required=True)

    args = parser.parse_args()

    itau = ItauScraper(args.agencia, args.conta, args.digito, args.senha)

    assert itau.login()

    data = itau.extrato()

    print(tabulate(data, headers=('Dia', 'Descrição', 'R$'), floatfmt='.2f'))
