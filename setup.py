#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = "Abdallah Deeb <abdallah@deeb.me>"
import os
from setuptools import setup
NAME = "RimuAPI"
GITHUB_URL = "https://github.com/abdallah/%s" % (NAME)
DESCRIPTION = "Python interface to RimuHosting API"

VERSION = "0.0.2"

REQUIREMENTS = ['requests']

setup(name=NAME,
              version=VERSION,
              download_url="%s/zipball/master" % GITHUB_URL,
              description=DESCRIPTION,
              install_requires=REQUIREMENTS,
              author='Abdallah Deeb',
              author_email='abdallah@deeb.me',
              url=GITHUB_URL,
              license='GPLv3+',
              py_modules=['rimuapi'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
        ],
      )


