# brightid-cli

The brightid-cli is a command line interface for BrightID.

## Installation

The brightid-cli can be installed using:

    $ sudo pip3 install brightidcli

It also can be installed from source with:

    $ git clone https://github.com/BrightID/brightid-cli
    $ cd brightid-cli
    $ python3 setup.py install


## Commands

### admin

Commands under `admin` namespace enable BrightID node admins manage their nodes

##### import-context

    $ brightid admin import-context --help
    Usage: brightid admin import-context [OPTIONS]

      Imports a new context to the node by getting contextIds linked under that
      context from a remote BrightID node

    Options:
      --context TEXT      The id of the context  [required]
      --remote-node TEXT  The address of the remote BrightID node  [required]
      --passcode TEXT     The one time passcode that the admin of the remote
                          BrightID node sets to authorize getting contextIds from
                          that node  [required]

##### set-passcode

    $ brightid admin set-passcode --help
    Usage: brightid admin set-passcode [OPTIONS]

      Sets a one time passcode on a context to authorize getting contextIds
      linked under that context by other nodes

    Options:
      --context TEXT   The id of the context  [required]
      --passcode TEXT  The one time passcode  [required]

##### set-sponsor-private-key

    $ brightid admin set-sponsor-private-key --help
    Usage: brightid admin set-sponsor-private-key [OPTIONS]

      Sets a private key that enables the node signing sponsor operations for an
      app

    Options:
      --app TEXT  The id of the app  [required]
      --key TEXT  The private key for signing sponsor operations  [required]

##### set-testing-key

    $ brightid admin set-testing-key --help
    Usage: brightid admin set-testing-key [OPTIONS]

      Sets a testing key on an app to enable its developers block getting
      verification for specific contextIds for testing purpose

    Options:
      --app TEXT  The id of the app  [required]
      --key TEXT  The testing key  [required]
      --help      Show this message and exit.

