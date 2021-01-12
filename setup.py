from setuptools import setup

setup(
    name='brightid-cli',
    version='0.1',
    py_modules=['brightid-cli'],
    install_requires=[
        'certifi==2020.12.5',
        'chardet==3.0.4',
        'click==7.1.2',
        'idna==2.10',
        'requests==2.25.0',
        'urllib3==1.26.2',
        'python-arango==5.4.0',
        'ed25519==1.5',
    ],
    entry_points='''
        [console_scripts]
        brightid-cli=main:cli
    ''',
)