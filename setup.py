#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import find_packages, setup
import ast
import re


def extract_version():
    with open('www/__init__.py', 'rb') as f_version:
        ast_tree = re.search(
            r'__version__ = (.*)',
            f_version.read().decode('utf-8')
        ).group(1)
        if ast_tree is None:
            raise RuntimeError('Cannot find version information')
        return str(ast.literal_eval(ast_tree))


with open('README.md', 'rb') as f_readme:
    readme = f_readme.read().decode('utf-8')

packages = find_packages()

version = extract_version()

setup(
    name="thinkPython",
    version=version,
    keywords=['www', 'network', 'framework', 'tcp_server', 'http_server'],
    description="A Strong Python Restful Service Framework",
    long_description=readme,
    author="Geek_Feng",
    author_email='759078664@qq.com',
    license="MIT",
    packages=packages,
    install_requires=['tornado', 'celery', 'redis', 'pymongo', 'requests', 'beautifulsoup4', 'pillow'],
    classifiers=[
        'Development Status :: 1 - Geek_Feng',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP/TCP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
