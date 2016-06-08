from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools import setup
import os
import sys
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve

# use requirements.txt as deps list
with open('requirements.txt') as f:
    required = f.read().splitlines()


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

setup(name='py-processors',
      version='2.1',
      keywords=['nlp', 'processors', 'jvm'],
      description="A wrapper for interacting with the CLU Lab's processors library.",
      url='http://github.com/myedibleenso/py-processors',
      author='myedibleenso',
      author_email='gushahnpowell@gmail.com',
      license='Apache',
      packages=["processors"],
      install_requires=required,
      cmdclass={
        'install': PyProcessorsInstall,
        'develop': PyProcessorsDevelop,
      },
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
