from setuptools import setup, find_packages

setup(
    name='brightidcli',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'certifi==2020.12.5',
        'chardet==3.0.4',
        'click==7.1.2',
        'idna==2.10',
        'requests==2.25.0',
        'urllib3==1.26.2',
        'python-arango==5.4.0',
        'ed25519==1.5',
        'python-brightid'
    ],
    entry_points='''
        [console_scripts]
        brightid=brightidcli.main:cli
    ''',
)