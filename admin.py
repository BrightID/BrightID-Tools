import sys
import time
import click
import requests
from arango import ArangoClient
from urllib.parse import urljoin


@click.group()
def main():
    "BrightID admin's CLI"
    pass


@main.command()
@click.option('--context', type=str, required=True, help="The context's key")
@click.option('--remote-node', type=str, required=True, help='The remote BrightID node')
@click.option('--passcode', type=str, required=True, help='The passcode of the context')
def add_context(context, remote_node, passcode):
    "Transferring a context's links from a remote BrightID node to the local node"
    print('Getting data...')

    db = ArangoClient().db('_system')
    variables = db.collection('variables')
    last_block = variables.get('LAST_BLOCK')['value']
    time.sleep(15)
    if last_block != variables.get('LAST_BLOCK')['value']:
        print('Error: You should stop the consensus receiver first')
        return

    response = requests.get(urljoin(remote_node, 'state')).json()
    if response.get('error'):
        print(f'Error: {response["errorMessage"]}')
        return

    if response['data']['lastProcessedBlock'] < last_block:
        print("Error: the local node's last processed block is greater than the last block of the remote node")
        return

    response = requests.get(
        urljoin(remote_node, f'contexts/{context}/dump?passcode={passcode}')).json()
    if response.get('error'):
        print(f'Error: {response["errorMessage"]}')
        return

    data = response['data']
    context_data = {
        '_key': context,
        'collection': data['collection'],
        'idsAsHex': data['idsAsHex'],
        'linkAESKey': data['linkAESKey']
    }

    print('Updating the local node...')
    # upsert the context
    if db['contexts'].get(context):
        db['contexts'].update(context_data)
    else:
        db['contexts'].insert(context_data)

    # create the collection, if not exists
    if db.has_collection(data['collection']):
        context_coll = db.collection(data['collection'])
    else:
        context_coll = db.create_collection(data['collection'])

    # insert the contextIds
    context_coll.import_bulk(data['contextIds'])
    print('Done')


@main.command()
@click.option('--context', type=str, required=True, help="The context's key")
@click.option('--passcode', type=str, required=True, help='The passcode of the context')
def set_passcode(context, passcode):
    "Add a one time passcode to the context document"

    db = ArangoClient().db('_system')
    context = db['contexts'].get(context)
    if not context:
        print(f'Error: context not found')
        return

    context['passcode'] = passcode
    db['contexts'].update(context)
    print('Done')


if __name__ == '__main__':
    main()
