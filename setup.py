#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   setup.py
@Time    :   2021/04/16 12:34:01
@Author  :   Xin Dong 
@Contact :   xindong9511@gmail.com
@License :   (C)Copyright 2020-2021, XinDong
'''

import os
import sys
import subprocess

# install giggle, tabix
# https://github.com/ryanlayer/giggle

def main():
    setup(
        name='SCRIPT',
        version='0.0.210520',
        author='Xin Dong',
        author_email='xindong9511@gmail.com',
        description='A package for single cell ATAC-seq analysis',
        packages=['SCRIPT', 'SCRIPT.enrichment', 'SCRIPT.conf', 'SCRIPT.utilities'],
        package_data={
        'SCRIPT': [
            'conf/config.yml',
            ],
        },
        install_requires=[
            'numba>=0.51.2',
            'numpy',
            'pandas>=1.1.1',
            'cython>=0.29.22',
            'ruamel.yaml',
            'anndata',
            'anndata2ri',
            # 'Bio',
            'pyranges==0.0.95',
            'pybedtools==0.8.1',
            'matplotlib',
            'seaborn',
            'sklearn',
            'scipy',
            'scanpy==1.7.1',
        ],
        python_requires='>=3.8.*, !=3.9.*',
        entry_points={
            'console_scripts': [
                'SCRIPT=SCRIPT.start:main'
            ]
        },
    )


if __name__ == "__main__":
    try:
        from setuptools import setup, find_packages
        main()
    except ImportError:
        print("Can not load setuptools!")
