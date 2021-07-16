Flask Thrift Client
##################

Introduction
============

This extension provide a simple intergration with
`Thrift <https://thrift.apache.org>`_ RPC server.

.. code:: python

    from flask import Flask
    from flask_thrift_client import Thrift_Client

    from MyGeneratedThriftCode import MyService

    app = Flask(__name__)
    app.config["THRIFTCLIENT_TRANSPORT"] = "tcp://127.0.0.1:9090"

    thriftclient = Thrift_Client(MyService.Client, app)

    @app.route("/")
    def home():
        data = thriftclient.client.mymethod()
        return data


Transport
=========

Thrift endpoints are defined in the configuration variable
THRIFTCLIENT_TRANSPORT as an URL. The default transport is
tcp://localhost:9090

Available url schemes are:

tcp: use TCP socket as transport, you have to define the server
address and port. If the port isn't defined, 9090 will be used

Example:

  * tcp://127.0.0.1

  * tcp://localhost:1234/


http: use HTTP protocol as transport. Examples:

  * http://myservice.local/

unix: use unix sockets as transport, as this scheme follow URI format,
it *MUST* have either no or three "/" before the socket path

  * unix:///tmp/mysocket #absolute path

  * unix:/tmp/mysocket #absolute path

  * unix:./mysocket #relative path

SSL
===

You may set SSL version of transport communications by using *'s'*
version of url scheme:

tcp <=> tcps
http <=> https
unix <=> unixs

examples:

  * https://myserver/

  * unixs:/tmp/mysocket

  * tcps://localhost:5533/

Two options are related to SSL transport:

THRIFTCLIENT_SSL_VALIDATE: True if the certificate has to be validated
(default True)

THRIFTCLIENT_SSL_CA_CERTS: path to the SSL certificate (default None)

Note that you *MUST* set one of theses options:

.. code:: python

    app.config["THRIFTCLIENT_SSL_VALIDATE"] = False
    app.config["THRIFTCLIENT_TRANSPORT"] = "https://127.0.0.1/"

    #or

    app.config["THRIFTCLIENT_SSL_CA_CERTS"] = "./cacert.pem"
    app.config["THRIFTCLIENT_TRANSPORT"] = "https://127.0.0.1/"

    #or
        
    app.config["THRIFTCLIENT_SSL_VALIDATE"] = True
    app.config["THRIFTCLIENT_TRANSPORT"] = "https://127.0.0.1/"

Protocol
========

You may define which procotol must be use by setting the parametter
*THRIFTCLIENT_PROTOCOL*. The default protocol is Binary.

Available parametters are:

Thrift_Client.BINARY or "BINARY" : use the binary protocol

Thrift_Client.COMPACT or "COMPACT" : use the compact protocol

Thrift_Client.JSON or "JSON" : use the JSON protocol. note that this
protocol is only available for thrift >= 0.9.1

Connection
==========

By default the application will open then close the transport for each request
This can be overriden by setting *THRIFTCLIENT_ALWAYS_CONNECT* to False

when THRIFTCLIENT_ALWAYS_CONNECT is set to False there is 3 ways to handle your
connections:

- you can call transport.close and transport.open manually
- you can use the autoconnect decorator
- you can use the connect "with" context

.. code:: python

    app = Flask(__name__)
    app.config["THRIFTCLIENT_TRANSPORT"] = "tcp://127.0.0.1:9090"
    app.config["THRIFTCLIENT_ALWAYS_CONNECT"] = False

    thriftclient = ThriftClient(MyService.Client, app)

    @app.route("/with_autoconnect")
    @thriftclient.autoconnect
    def with_autoconnect():
        data = thriftclient.client.mymethod()
        return data

    @app.route("/with_context")
    def with_context():
        with thriftclient.connect():
            data = thriftclient.client.mymethod()
            return data

    @app.route("/with_manual_connection")
    def with_manual_connection():
        thriftclient.transport.open()
        data = thriftclient.client.mymethod()
        thriftclient.transport.close()
        return data

Options
=======

Other options are:

THRIFTCLIENT_BUFFERED: use buffered transport (default False)

THRIFTCLIENT_ZLIB: use zlib compressed transport (default False)

THRIFTCLIENT_BUFFERED: use buffered transport (default False)
