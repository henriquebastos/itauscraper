"""Command line interface."""
import argparse

from tabulate import tabulate

from itauscraper.scraper import ItauScraper


def main():
    parser = argparse.ArgumentParser(prog='itau', description='Scraper de extrato do Itaú.')

    parser.add_argument('--agencia', '--ag', '-a', help='Agência na forma 0000', required=True)
    parser.add_argument('--conta', '--cc', '-c', help='Conta sem dígito na forma 00000', required=True)
    parser.add_argument('--digito', '--dv', '-d', help='Dígito da conta na forma 0', required=True)
    parser.add_argument('--senha', help='Senha eletrônica da conta no Itaú.', required=True)

    args = parser.parse_args()

    itau = ItauScraper(args.agencia, args.conta, args.digito, args.senha)

    assert itau.login()

    data = itau.extrato()

    print(tabulate(data, headers=('Dia', 'Descrição', 'R$'), floatfmt='.2f'))
