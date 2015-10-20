#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    description='RESTful Nagios/Icinga Livestatus API',
    author='Christoph Oelmueller',
    url='https://github.com/zwopiR/lsapi',
    download_url='https://github.com/zwopiR/lsapi',
    author_email='christoph@oelmueller.info',
    version='0.1',
    install_requires=['flask', 'ConfigParser'],
    tests_require=['mock', 'nose'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    scripts=[],
    name='lsapi'
)
