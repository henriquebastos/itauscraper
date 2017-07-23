"""Command line interface."""
import argparse

from tabulate import tabulate

from itauscraper.scraper import ItauScraper


def main():
    parser = argparse.ArgumentParser(prog='itau',
                                     description='Scraper para baixar seus extratos do Itaú com um comando.')

    parser.add_argument('--extrato', action='store_true', help='Lista extrato da conta corrente.')
    parser.add_argument('--cartao', action='store_true', help='Lista extrato do cartão de crédito.')
    parser.add_argument('--agencia', '-a', help='Agência na forma 0000', required=True)
    parser.add_argument('--conta', '-c', help='Conta sem dígito na forma 00000', required=True)
    parser.add_argument('--digito', '-d', help='Dígito da conta na forma 0', required=True)
    parser.add_argument('--senha', '-s', help='Senha eletrônica da conta no Itaú.', required=True)

    args = parser.parse_args()

    if not (args.extrato or args.cartao):
        parser.exit(0, "Indique a operação: --extrato e/ou --cartao\n")

    itau = ItauScraper(args.agencia, args.conta, args.digito, args.senha)

    assert itau.login()

    if args.extrato:
        data = itau.extrato()
        print(tabulate(data, headers=('Dia', 'Descrição', 'R$'), floatfmt='.2f'))

    if args.cartao:
        summary, data = itau.cartao()
        print(tabulate(summary.items(), floatfmt='.2f'))
        print(tabulate(data, headers=('Dia', 'Descrição', 'Valor'), floatfmt='.2f'))
