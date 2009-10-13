from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='thingsapp',
      version=version,
      description="Things.app utility scripts",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Sridhar Ratnakumar',
      author_email='srid@nearfar.org',
      url='http://workspace.activestate.com/sridharr/thingsapp',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'appscript',
          'cmdln',
      ],
      entry_points={
        'console_scripts':
            ['thingsapp-dump=thingsapp:play']
        }
      )
