import sys
import os
import socket
import base64
import time
import click
import ed25519
import requests
from arango import ArangoClient
from urllib.parse import urljoin

def get_db():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = os.environ.get('BN_ARANGO_HOST', 'localhost')
    port = int(os.environ.get('BN_ARANGO_PORT', 8529))
    result = sock.connect_ex((host, port))
    sock.close()
    if result != 0:
        print(f'Arango database is not running on {host}:{port}. The host and the port for accessing database can be configured using BN_ARANGO_HOST and BN_ARANGO_PORT env variables.')
        sys.exit()

    return ArangoClient(hosts=f'http://{host}:{port}').db('_system')

@click.group()
def admin():
    "Commands for BrightID node admins"
    pass


@admin.command()
@click.option('--context', type=str, required=True, help='The id of the context')
@click.option('--remote-node', type=str, required=True, help='The address of the remote BrightID node, e.g. http://node.brightid.org')
@click.option('--passcode', type=str, required=True, help='The one time passcode that the admin of the remote BrightID node sets to authorize getting contextIds from that node')
def import_context(context, remote_node, passcode):
    "Imports a new context to the node by getting contextIds linked under that context from a remote BrightID node"

    db = get_db()
    variables = db.collection('variables')
    last_block = variables.get('LAST_BLOCK')['value']
    url = urljoin(remote_node, '/brightid/v5/state')
    try:
        state = requests.get(url).json()['data']
    except:
        return print(f'Error: {url} is not a valid remote node address or is not accessible')

    if state['lastProcessedBlock'] < last_block:
        return print("Error: The state of remote node is older than local's one. Try again after the remote node synced.")

    print('Checking if the consensus receiver is stopped ...')
    time.sleep(10)
    if last_block != variables.get('LAST_BLOCK')['value']:
        return print('Error: The consensus receiver is not stopped. Stop it using following command and try again.\n$ docker-compose stop consensus_receiver')

    print('Getting data...')
    url = urljoin(remote_node, f'/brightid/v5/contexts/{context}/dump?passcode={passcode}')
    res = requests.get(url).json()
    if res.get('error'):
        return print(f'Error: {res["errorMessage"]}')

    data = res['data']
    context_data = {
        '_key': context,
        'collection': data['collection'],
        'idsAsHex': data['idsAsHex'],
        'linkAESKey': data['linkAESKey']
    }

    print('Importing context ...')
    # upsert the context
    if db['contexts'].get(context):
        db['contexts'].update(context_data)
    else:
        db['contexts'].insert(context_data)

    # create the collection, if not exists
    if db.has_collection(data['collection']):
        contextIds_coll = db.collection(data['collection'])
        contextIds_coll.truncate()
    else:
        contextIds_coll = db.create_collection(data['collection'])

    # insert the contextIds
    contextIds_coll.import_bulk(data['contextIds'])
    print('Done')


@admin.command()
@click.option('--context', type=str, required=True, help='The id of the context')
@click.option('--passcode', type=str, required=True, help='The one time passcode')
def set_passcode(context, passcode):
    "Sets a one time passcode on a context to authorize getting contextIds linked under that context by other nodes"

    db = get_db()
    context = db['contexts'].get(context)
    if not context:
        return print('Error: context not found')

    context['passcode'] = passcode
    db['contexts'].update(context)
    print('Done')


@admin.command()
@click.option('--app', type=str, required=True, help="The id of the app")
@click.option('--key', type=str, required=True, help="The private key for signing sponsor operations")
def set_sponsor_private_key(app, key):
    "Sets a private key that enables the node signing sponsor operations for an app"

    db = get_db()
    app = db['apps'].get(app)
    if not app:
        return print('Error: app not found')

    try:
        private = base64.b64decode(key)
        public = ed25519.SigningKey(private).get_verifying_key().to_bytes()
        public = base64.b64encode(public).decode('ascii')
        assert public == app['sponsorPublicKey']
    except Exception as e:
        return print("Private key does not match the app's sponsor public key")

    app['sponsorPrivateKey'] = key
    db['apps'].update(app)
    print('Done')


@admin.command()
@click.option('--app', type=str, required=True, help="The id of the app")
@click.option('--key', type=str, required=True, help="The testing key")
def set_testing_key(app, key):
    "Sets a testing key on an app to enable its developers block getting verification for specific contextIds for testing purpose"

    db = get_db()
    app = db['apps'].get(app)
    if not app:
        return print('Error: app not found')

    app['testingKey'] = key
    db['apps'].update(app)
    print('Done')
