from setuptools import setup
import os

# use requirements.txt as deps list
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='py-processors',
      version='1.0',
      include_package_data=True,
      keywords=['nlp', 'processors', 'jvm'],
      description="A wrapper for interacting with the CLU Lab's processors library.",
      url='http://github.com/myedibleenso/py-processors',
      author='myedibleenso',
      author_email='gushahnpowell@gmail.com',
      license='Apache',
      packages=["processors"],
      install_requires=required,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
