#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from simpleflow import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()


setup(
    install_requires=('eventlet>=0.18.4',
                      'six>=1.9.0',
                      'enum34',
                      'networkx>=1.9.2',
                      'simpleutil>=1.0',
                      'simpleutil<1.1',
                      'simpleservice>=1.0',
                      'simpleservice<1.0',
                      ),
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
    packages=find_packages(include=['simpleflow*']),
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
