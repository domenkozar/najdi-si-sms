import sys
import os

from setuptools import setup
from setuptools import find_packages

version = '0.1'

setup(name='najdisi-sms',
      version=version,
      description="Najdi.si sms command line sender",
      long_description="""""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Domen Kozar',
      author_email='domen@dev.si',
      url='',
      license='BSD',
      py_modules=['najdisi_sms'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'mechanize',
      ],
      entry_points="""
      [console_scripts]
      najdisi-sms = najdisi_sms:main
      """,
      )
