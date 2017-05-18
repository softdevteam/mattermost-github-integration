# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join
from setuptools import find_packages, setup
import codecs


def read_relative_file(filename):
    """
    Returns contents of the given file, whose path is supposed relative
    to this module.
    """
    with codecs.open(join(dirname(abspath(__file__)), filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='mattermost-github',
    version="0.1.0",
    author='Mattermost Github Integration Developers',
    author_email='info@soft-dev.org',
    packages=["mattermostgithub"],
    include_package_data=True,
    long_description=read_relative_file('README.md'),
    url='https://github.com/softdevteam/mattermost-github-integration',
    license='MIT',
    description='Integration between Mattermost and Github',
    zip_safe=False,
    install_requires=[
        "Flask>=0.12.1",
        "Pillow>=4.1.1",
        "requests>=2.13.0",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
