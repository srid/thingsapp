from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='thingsapp',
      version=version,
      description="Python bindings for accessing Things.app",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='gtd things mac',
      author='Sridhar Ratnakumar',
      author_email='github@srid.name',
      url='http://github.com/srid/thingsapp',
      license='MIT',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'appscript',
          'jinja2',
      ],
      entry_points={
        'console_scripts':
            ['thingsapp-dump=thingsapp:play']
        }
      )
