# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
from setuptools import setup, find_packages

setup(
    name='tsl-dependencies',
    version='1.0',
    packages=find_packages(),
    install_requires=['selenium', 'pandas', 'bs4', 'colorama']
)