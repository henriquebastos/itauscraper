Itaú Scraper
============

Scraper para baixar seus extratos do Itaú com um comando.

Motivação
---------

As APIs vieram para ficar, mas a maioria dos bancos ainda não oferecem forma
fácil para seus clientes extraírem seus próprios dados. Algo tão simples
quanto obter o seu extrato bancário é um sofrimento para sistematizar.

Pesquisei se existia algo pronto para o Itaú e encontrei o
`bankscraper <https://github.com/kamushadenes/bankscraper>`_ do
`Kamus <http://endurance.hyadesinc.com/>`_ que disponibiliza vários scripts
interessantes. Infelizmente o do Itaú não estava mais funcionando,
mas estudando seu código encontrei uma boa dica:

    O site do Itaú para computador é todo complicado para navegar com muita
    mágica em javascript. Mas e o site para disponsitivos móveis?

Ativei o `"mobile mode" <https://developers.google.com/web/tools/chrome-devtools/device-mode/>`_
do Chrome com o `Postman <https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop>`_
e o `Postman Interceptor <https://chrome.google.com/webstore/detail/postman-interceptor/aicmkgpgakddgnaphhhpliifpcfhicfo>`_
para rastrear todas as requisições e **bingo**. De fato é bem mais simples.

Decidi escrever este artigo para explicar o procedimento, evidenciar as
bizarrices e quem sabe facilitar a manutenção futura quando algo mudar.

Este script funciona apenas para contas *Pessoa Física*, pois o Itaú força
empresas a usarem seu aplicativo no celular não dando acesso ao site móvel
pelo navegador.

Como funciona
~~~~~~~~~~~~~

O código é simples e usa `Python 3 <https://www.python.org/>`_ com a biblioteca
`requests <http://docs.python-requests.org/en/master/>`_ para a navegação
e `lxml <http://lxml.de/>`_ para a extração de dados com
`xpath <http://ricostacruz.com/cheatsheets/xpath.html>`_.

Mais do que explicar o código em si, o importante é entender o fluxo de
navegação que ele precisa reproduzir.

O protocolo HTTP é *assíncrono* exigindo que cada requisição envie novamente
todas as informações necessárias. No entanto, o site do banco cria uma dinâmica
cliente-servidor estabelecendo dependência entre as requisições mudando inclusive
as urls de navegação. Por isso todo o processo acontece sequencialmente, cheio de
etapas intermediárias que não seriam necessárias em condições normais.

Usando o ``requests.Session`` conseguimos reproduzir o efeito de navegação contínua
entre várias páginas propagando *cookies* e outros *cabeçalhos*.

A classe ``MobileSession`` implementa os cabeçalhos para nos fazermos
passar por um browser de celular.

A classe ``ItauScraper`` usa a ``session`` para realizar o ``login`` e
consultar o ``extrato``.

O login
~~~~~~~

Para fazer o ``login`` no site do banco é preciso acessar uma url inicial para
descobrirmos a url de login real, que muda de tempos em tempos pelo que eu entendi.

Com a *url de login* correta, agora é preciso fazer um novo ``GET`` para obter
informações que o ASP.NET injeta no formulário de login e então realizar o POST
efetuando a autenticação.

Depois do login feito, somos redirecionados para uma página com um menu de
navegação. Esta página não é usada no fluxo, mas quando quisermos implementar novas
funcionalidades no ``ItauScraper`` é nela que deveremos começar.

.. image:: https://raw.githubusercontent.com/henriquebastos/itauscraper/master/docs/itau-login.jpg

O extrato
~~~~~~~~~

Quando acessamos a *url do extrato*, por padrão é exibido o extrato dos *últimos 3 dias*.
No fim da página do extrato tem 4 links para listar os extratos dos períodos
7, 15, 30 e 90 dias. Estas urls parecem mudar de tempos em tempos, como a do login,
então é preciso *extrair o link* para *90 dias* e obter o extrato com outro ``GET``.

.. image:: https://raw.githubusercontent.com/henriquebastos/itauscraper/master/docs/itau-extrato.jpg

Com o extrato do maior período:

1. Extraímos a informação do html;
2. Reconstruímos a tabela com as colunas: data, descrição e valor;
3. Filtramos as linhas de saldo que não correspondem a um lançamento;
4. Convertemos cada *data* para o tipo ``datetime.date``;
5. Convertemos cada *valor* para o tipo ``Decimal``;

No final, temos uma *tupla de tuplas* na forma:

.. code-block:: python

    ((datetime.datetime(2017, 1, 1, 0, 0), 'RSHOP-LOJA1', Decimal('-1.99')),
     (datetime.datetime(2017, 1, 2, 0, 0), 'RSHOP-LOJA2', Decimal('-5.00')),
     (datetime.datetime(2017, 1, 3, 0, 0), 'TBI 1234567', Decimal('10.00')))

Como usar
---------

Use pela linha de comando:

.. code-block:: console

 $ itauscraper --agencia 1234 --conta 12345 --digito 6 --senha SECRET

 Dia                  Descrição            R$
 -------------------  -----------  ----------
 2017-01-01 00:00:00  RSHOP-LOJA1       -1.99
 2017-01-02 00:00:00  RSHOP-LOJA2       -5.00
 2017-01-03 00:00:00  TBI 1234567       10.00

Ou importe direto no seu código:

.. code-block:: python

 from itauscraper import ItauScraper

 itau = ItauScraper(agencia='1234', conta='12345', digito='6', senha='SECRET')
 if itau.login():
     dados = itau.extrato()
     # TODO: Divirta-se!

Development
-----------

.. code-block:: console

 git clone https://github.com/henriquebastos/itauscraper.git
 cd itauscraper
 python -m venv -p python3.6 .venv
 source .venv/bin/activate
 pip install -r requirements.txt


Licença
-------

Copyright (C) 2017 Henrique Bastos.

Este código é distribuído nos termos da "GNU GPLv3". Veja o arquivo LICENSE para detalhes.
