#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    description='RESTful Nagios/Icinga Livestatus API',
    author='Christoph Oelmueller',
    url='URL to get it at.',
    download_url='Where to download it.',
    author_email='christoph@oelmueller.info',
    version='0.1',
    install_requires=['nose', 'paramiko', 'flask', 'ConfigParser'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    scripts=[],
    name='lsapi'
)
