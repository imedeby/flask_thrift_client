from thrift.transport import TSocket, THttpClient, TTransport, TZlibTransport, TSSLSocket
from thrift.protocol import TBinaryProtocol, TCompactProtocol
try:
	#only available from thrift >= 0.9.1
	from thrift.protocol import TJSONProtocol

	HAS_JSON_PROTOCOL = True
except ImportError:
	HAS_JSON_PROTOCOL = False

from urllib.parse import urlparse
from functools import wraps
from contextlib import contextmanager
import ssl

class Thrift_Client(object):

	BINARY = "BINARY"
	COMPACT = "COMPACT"
	if HAS_JSON_PROTOCOL:
		JSON = "JSON"

	def __init__(self, interface, app=None, config=None):
		self.interface = interface
		self.protocol = None
		self.transport = None
		self.client = None
		self.config = config
		self.alwaysConnect = True
		if app is not None:
			self.init_app(app)

	def init_app(self, app, config=None):
		if not config:
			config = self.config
		if not config:
			config = app.config

		config.setdefault("THRIFTCLIENT_TRANSPORT", "tcp://localhost:9090")
		config.setdefault("THRIFTCLIENT_PROTOCOL", Thrift_Client.BINARY)

		config.setdefault("THRIFTCLIENT_SSL_VALIDATE", True)
		config.setdefault("THRIFTCLIENT_SSL_CA_CERTS", None)

		config.setdefault("THRIFTCLIENT_BUFFERED", False)
		config.setdefault("THRIFTCLIENT_ZLIB", False)

		config.setdefault("THRIFTCLIENT_ALWAYS_CONNECT", True)

		self._set_client(app, config)

		if self.alwaysConnect:
			@app.before_request
			def before_request():
				assert(self.client is not None)
				assert(self.transport is not None)
				try:
					self.transport.open()
				except TTransport.TTransportException:
					raise RuntimeError("Unable to connect to thrift server")

			@app.teardown_request
			def after_request(response):
				self.transport.close()

	@contextmanager
	def connect(self):
		assert(self.client is not None)
		assert(self.transport is not None)
		
		try:
			self.transport.open()
		except TTransport.TTransportException:
			raise RuntimeError("Unable to connect to thrift server")

		yield

		self.transport.close()


	def autoconnect(self, func):
		"""
		when using THRIFTCLIENT_ALWAYS_CONNECT at false, this decorator allows
		to connect to the thrift service automatically for a single function
		"""
		@wraps(func)
		def onCall(*args, **kwargs):
			#we don't want to connect twice
			if self.alwaysConnect:
				return func(*args, **kwargs)
			with self.connect():
				return func(*args, **kwargs)
		return onCall

	def _set_client(self, app, config):
		#configure thrift thransport
		"""
		when using THRIFTCLIENT_SSL_VALIDATE at true with tcps connection, we can test ssl trust between server and client with ca certificate
		otherwise we cen connect without using ca certificate , we will try connect using cert_none
		"""
		if config["THRIFTCLIENT_TRANSPORT"] is None:
			raise RuntimeError("THRIFTCLIENT_TRANSPORT MUST be specified")
		uri = urlparse(config["THRIFTCLIENT_TRANSPORT"])
		if uri.scheme == "tcp":
			port = uri.port or 9090
			self.transport = TSocket.TSocket(uri.hostname, port)
		elif uri.scheme == "tcps":
			port = uri.port or 9090
			if not (config["THRIFTCLIENT_SSL_VALIDATE"]) : 
				self.transport = TSSLSocket.TSSLSocket(
					host=uri.hostname,
					port=port,
					cert_reqs=ssl.CERT_NONE
				)
			else:
				self.transport = TSSLSocket.TSSLSocket(
				    host=uri.hostname,
					port=port,
					validate = config["THRIFTCLIENT_SSL_VALIDATE"],
					ca_certs  = config["THRIFTCLIENT_SSL_CA_CERTS"],
				)
		elif uri.scheme in ["http", "https"]:
			self.transport = THttpClient.THttpClient(config["THRIFTCLIENT_TRANSPORT"])
		elif uri.scheme == "unix":
			if uri.hostname is not None:
				raise RuntimeError("unix socket MUST starts with either unix:/ or unix:///")
			self.transport = TSocket.TSocket(unix_socket=uri.path)
		elif uri.scheme == "unixs":
			if uri.hostname is not None:
				raise RuntimeError("unixs socket MUST starts with either unixs:/ or unixs:///")
			self.transport = TSSLSocket.TSSLSocket(
				validate = config["THRIFTCLIENT_SSL_VALIDATE"],
				ca_certs  = config["THRIFTCLIENT_SSL_CA_CERTS"],
				unix_socket = uri.path)
		else:
			raise RuntimeError(
				"invalid configuration for THRIFTCLIENT_TRANSPORT: {transport}"
				.format(transport = config["THRIFTCLIENT_TRANSPORT"])
				)
		"""
		Adding protocol layer THRIFTCLIENT_FRAMED 
		"""
		#configure additionnal protocol layers
		if config["THRIFTCLIENT_BUFFERED"] == True:
			self.transport = TTransport.TBufferedTransport(self.transport)
		if config["THRIFTCLIENT_ZLIB"] == True:
			self.transport = TZlibTransport.TZlibTransport(self.transport)
		if config["THRIFTCLIENT_FRAMED"] == True:
			self.transport = TTransport.TFramedTransport(self.transport)

		#configure thrift protocol
		if config["THRIFTCLIENT_PROTOCOL"] == Thrift_Client.BINARY:
			self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
		elif config["THRIFTCLIENT_PROTOCOL"] == Thrift_Client.COMPACT:
			self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
		elif HAS_JSON_PROTOCOL and config["THRIFTCLIENT_PROTOCOL"] == Thrift_Client.JSON:
			self.protocol = TJSONProtocol.TJSONProtocol(self.transport)
		else:
			raise RuntimeError(
				"invalid configuration for THRIFTCLIENT_PROTOCOL: {protocol}"
				.format(protocol = config["THRIFTCLIENT_PROTOCOL"])
				)

		#create the client from the interface
		self.client = self.interface(self.protocol)

		#configure auto connection
		self.alwaysConnect = config["THRIFTCLIENT_ALWAYS_CONNECT"]