# -*- coding: utf-8 -*-
# import sys
from os.path import join, dirname, exists
from setuptools import setup
from setuptools import find_packages

long_description = open(join(dirname(__file__), 'README.md')).read().strip() if exists('README.md') else ''
_locals = {}
with open("ssh_config/version.py") as f:
    exec(f.read(), None, _locals)
version = _locals["__version__"]

install_requires = [
    "pyparsing",
    "docopt",
    "texttable",
    "Jinja2",
]

setup(
    name="ssh_config",
    description="ssh client config manager",
    license="MIT License",
    url="https://github.com/haginara/ssh_config",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=version,
    author="Jonghak Choi",
    author_email="haginara@gmail.com",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'ssh-config=ssh_config.cli2:main',
        ]
    },
    packages=find_packages(),
    package_data={
        '': ['README.md', 'LICENSE'],
    },
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
