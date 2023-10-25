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
    install_requires=['tk==0.1.0', 'selenium==4.9.0', 'pandas==2.1.0', 'bs4==0.0.1', 'colorama==0.4.6']
)