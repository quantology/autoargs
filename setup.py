try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import autoargs

classifiers = [
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "Development Status :: 3 - Alpha",
    "Operating System :: OS Independent",
    "Topic :: Software Development",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: System :: Shells",
]

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(name="autoargs",
      version=autoargs.__version__,
      author="Michael Tartre",
      author_email="metaperture@gmail.com",
      url="https://github.com/metaperture/autoargs",
      py_modules=["autoargs"],
      description="Automatic Arg parsing",
      long_description=long_description,
      license="MIT",
      classifiers=classifiers
      )
