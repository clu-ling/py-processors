#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from codecs import open
try:
    import urllib.request as urlrequest
except ImportError:
    import urllib as urlrequest
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools import setup
import re
import os
import sys


class JarManager(object):

    ppjar = os.path.join("processors", "processors-server.jar")

    @classmethod
    def download_jar(cls):
        # download processors-server.jar
        ppjar = JarManager.ppjar
        percent = 0
        def dlProgress(count, blockSize, totalSize):
            percent = int(count*blockSize*100/totalSize)
            sys.stdout.write("\r{}% complete".format(percent))
            sys.stdout.flush()
        jar_url = "http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar"
        print("Downloading {} from {} ...".format(ppjar, jar_url))
        urlretrieve(jar_url, ppjar, reporthook=dlProgress)
        print("\nInstalling py-processors ...")

class PyProcessorsDevelop(develop):

    def run(self):
        # download processors-server.jar
        #JarManager.download_jar()
        develop.run(self)

class PyProcessorsInstall(install):
    """Downloads processors-server.jar for use in py-processors"""

    def run(self):
        # download processors-server.jar
        #JarManager.download_jar()
        # install everything else
        install.run(self)

# use requirements.txt as deps list
with open('requirements.txt', 'r', 'utf-8') as f:
    required = f.read().splitlines()

# get readme
with open('docs/index.md', 'r', 'utf-8') as f:
    readme = f.read()

# get version
with open('processors/__init__.py', 'r', 'utf-8') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(name='py-processors',
      packages=["processors"],
      version=version,
      keywords=['nlp', 'processors', 'jvm'],
      description="A wrapper for interacting with the CLU Lab's processors library.",
      long_description=readme,
      url='http://github.com/myedibleenso/py-processors',
      download_url="https://github.com/myedibleenso/py-processors/archive/v{}.zip".format(version),
      author='myedibleenso',
      author_email='gushahnpowell@gmail.com',
      license='Apache 2.0',
      install_requires=required,
      cmdclass={
        'install': PyProcessorsInstall,
        'develop': PyProcessorsDevelop,
      },
      classifiers=(
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
      ),
      tests_require=['green', 'coverage'],
      include_package_data=True,
      zip_safe=False)
