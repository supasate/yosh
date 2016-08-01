#!/usr/bin/env python

from setuptools import setup

setup(name='yosh',
      version='1.0',
      description='Your own shell',
      author='Supasate Choochaisri',
      author_email='supasate.c@gmail.com',
      url='https://github.com/supasate/yosh',
      packages=['yosh', 'yosh.builtins'],
      entry_points="""
      [console_scripts]
      yosh = yosh.shell:main
      """,
      )
