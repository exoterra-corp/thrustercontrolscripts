#!/usr/bin/venv python3
from distutils.core import setup
from setuptools import find_packages

setup(name='thrustercontrolscripts',
      version='2.0.1',
      description='Python System Controller Support Library.',
      author='Jeremy Mitchell',
      author_email='jmitchell@exoterracorp.com',
      scripts=['thruster_command.py', 'listener.py'],
      packages=find_packages() #['tcsrc'],
)