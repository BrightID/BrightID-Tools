import sys
import click
import config
from urllib.parse import urljoin
from arango import ArangoClient
import requests


@click.group()
def main():
    "Simple CLI for transferring a context's links form a remote BrightID node to the local node"
    pass


@main.command()
@click.option('--context-key', type=str, required=True, help='The context key')
@click.option('--passcode', type=str, required=True, help='The passcode of the context')
@click.option('--node-url', type=str, help='The remote BrightID node')
def run(context_key, passcode, node_url):
    "Load the context data on the local node"

    if not node_url:
        node_url = config.NODE_ONE_URL
    url = urljoin(node_url,
        f'{config.BRIGHTID_VERSION}/contexts/{context_key}/dump?passcode={passcode}')
    response = requests.get(url).json()
    if response.get('error'):
        print('Error: ', response['errorMessage'])
        return

    data = response['data']
    context = {
        '_key': context_key,
        'collection': data['collection'],
        'idsAsHex': data['idsAsHex'],
        'linkAESKey': data['linkAESKey']
    }

    print('Updating the local node...')
    db = ArangoClient().db('_system')
    # upsert the context
    if db['contexts'].get(context_key):
        db['contexts'].update(context)
    else:
        db['contexts'].insert(context)

    # create the collection, if not exists
    if db.has_collection(data['collection']):
        context_coll = db.collection(data['collection'])
    else:
        context_coll = db.create_collection(data['collection'])

    # insert the contextIds
    context_coll.import_bulk(data['contextIds'])
    print('Done')


if __name__ == '__main__':
    main()
