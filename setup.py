#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md', encoding='utf-8') as history_file:
    history = history_file.read()

install_requires = [
    "numpy",
]

setup_requires = [
    'pytest-runner>=2.11.1',
]

tests_require = [
    'pytest>=3.4.2',
    'pytest-cov>=2.6.0',
]

development_requires = [
    # general
    'bumpversion>=0.5.3',
    'pip>=9.0.1',
    'watchdog>=0.8.3',

    # docs
    'm2r>=0.2.0,<0.3',
    'Sphinx>=1.7.1,<3',
    'sphinx_rtd_theme>=0.2.4,<0.5',
    'autodocsumm>=0.1.10',

    # style check
    'flake8>=3.7.7',
    'isort>=4.3.4',

    # fix style issues
    'autoflake>=1.2',
    'autopep8>=1.4.3',

    # distribute on PyPI
    'twine>=1.10.0',
    'wheel>=0.30.0',

    # Advanced testing
    'coverage>=4.5.1',
    'tox>=2.9.1',
]

setup(
    author='Manuel Alvarez',
    author_email='manuel@pythiac.com',
        description='Augmented reality Piano using Kinnect camera',
    extras_require={
        'test': tests_require,
        'dev': development_requires + tests_require,
    },
    install_package_data=True,
    install_requires=install_requires,
    license='GNU General Public License v3',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='keyboard_anywhere keyboard_anywhere keyboard_anywhere',
    name='keyboard_anywhere',
    packages=find_packages(include=['keyboard_anywhere', 'keyboard_anywhere.*']),
    python_requires='>=3.4',
    setup_requires=setup_requires,
    test_suite='tests',
    tests_require=tests_require,
    url='https://github.com/ManuelAlvarezC/keyboard_anywhere',
    version='0.0.0.dev0',
    zip_safe=False,
)
