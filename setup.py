#!/usr/bin/env python
"""
Flask-ThriftClient
-----------

Adds thrift client support to your Flask application

"""

import os
from setuptools import setup

here = os.path.dirname(__file__)
readme_path = os.path.join(here, 'README.md')
long_description = ""
with open(readme_path) as fd:
	long_description = fd.read()


setup(
	name='Flask-Thrift_Client',
	version='0.1.0',
	url='https://github.com/imedeby/flask_thrift_client.git',
	description='Adds thrift client support to your Flask application',
	long_description=long_description,
	packages=[
		'flask_thrift_client',
	],
	zip_safe=False,
	platforms='any',
	install_requires=[
		'Flask>=0.7',
		'thrift>=0.8'
	],
	test_suite='tests.thrift_client',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Framework :: Flask',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)
