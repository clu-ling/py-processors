#!/usr/bin/env python

from codecs import open
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools import setup
import re
import os
import sys
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve


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
        print("Installing py-processors ...")

class PyProcessorsDevelop(develop):

    def run(self):
        # download processors-server.jar
        JarManager.download_jar()
        develop.run(self)

class PyProcessorsInstall(install):
    """Downloads processors-server.jar for use in py-processors"""

    def run(self):
        # download processors-server.jar
        JarManager.download_jar()
        # install everything else
        install.run(self)

# use requirements.txt as deps list
with open('requirements.txt') as f:
    required = f.read().splitlines()

# get readme
with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

# get version
with open('processors/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(name='py-processors',
      version=version,
      keywords=['nlp', 'processors', 'jvm'],
      description="A wrapper for interacting with the CLU Lab's processors library.",
      long_description=readme,
      url='http://github.com/myedibleenso/py-processors',
      author='myedibleenso',
      author_email='gushahnpowell@gmail.com',
      license='Apache 2.0',
      packages=["processors"],
      install_requires=required,
      cmdclass={
        'install': PyProcessorsInstall,
        'develop': PyProcessorsDevelop,
      },
      include_package_data=True,
      zip_safe=False)
