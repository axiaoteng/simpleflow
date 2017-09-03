#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

from simpleflow import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

'enum34'
'jsonschema!=2.5.0,<3.0.0,>=2.0.0'

setup(
    install_requires=('eventlet>=0.15.2',
                      'sqlalchemy>=1.0.11',
                      'six>=1.9.0',
                      'networkx>=1.10',
                      'simpleutil>=1.0.0',
                      'simpleservice>=1.0.0'),
    name='simpleflow',
    version=__version__,
    description='a simple copy of taskflow 1.30 from openstack',
    long_description=long_description,
    url='http://github.com/lolizeppelin/simpleflow',
    author='Lolizeppelin',
    author_email='lolizeppelin@gmail.com',
    maintainer='Lolizeppelin',
    maintainer_email='lolizeppelin@gmail.com',
    keywords=['simpleflow'],
    license='MIT',
    packages=['simpleflow'],
    # tests_require=['pytest>=2.5.0'],
    # cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
