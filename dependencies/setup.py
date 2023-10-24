# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
from setuptools import setup, find_packages

setup(
    name='tsl-dependencies',
    version='1.1',
    packages=find_packages(),
    install_requires=['tk', 'selenium', 'pandas==2.1.0', 'bs4', 'colorama']
)