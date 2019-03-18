# -*- coding: utf-8 -*-
# import sys
from os.path import join, dirname, exists
from setuptools import setup
from setuptools import find_packages

from ssh_config import __version__
long_description = open(join(dirname(__file__), 'README.md')).read().strip() if exists('README.md') else ''
install_requires = [
    "pyparsing",
    "docopt",
]

setup(
    name="ssh_config",
    description="ssh client config manager",
    license="MIT License",
    url="http://www.haginara.com",
    long_description=long_description,
    version=str('.'.join(map(str, __version__))),
    author="Jonghak Choi",
    author_email="haginara@gmail.com",
    entry_points={
        'console_scripts': [
            'ssh_config=ssh_config.cli:main',
        ]
    },
    packages=find_packages(),
    package_data={
        '': ['*.txt', '*.md'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=install_requires,
)
