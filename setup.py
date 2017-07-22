# coding: utf-8
from setuptools import setup
import os


README = os.path.join(os.path.dirname(__file__), 'README.rst')
REQUIREMENTS = os.path.join(os.path.dirname(__file__), 'requirements.txt')


if __name__ == "__main__":
    setup(name='itauscraper',
          description='Scraper para baixar seus extratos do Itaú com um comando.',
          version='0.2',
          long_description=open(README).read(),
          author="Henrique Bastos", author_email="henrique@bastos.net",
          license="GNU GPLv3",
          url='http://github.com/henriquebastos/itauscraper/',
          keywords=['scraper', 'requests', 'lxml', 'itau', 'bank', 'finance', 'accounting'],
          install_requires=open(REQUIREMENTS).readlines(),
          packages=['itauscraper'],
          package_dir={"itauscraper": "itauscraper"},
          entry_points={
              'console_scripts': [
                  'itauscraper = itauscraper.cli:main',
              ]
          },
          zip_safe=False,
          platforms='any',
          include_package_data=True,
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: Financial and Insurance Industry',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Natural Language :: English',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3 :: Only',
              'Topic :: Office/Business :: Financial :: Accounting',
              'Topic :: Utilities',
          ])
