try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import autoargs

classifiers = [
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(name="six",
      version=autoargs.__version__,
      author="Michael Tartre",
      author_email="mtartre@gmail.com",
      url="https://github.com/metaperture/autoargs",
      py_modules=["autoargs"],
      description="Automatic Arg parsing",
      long_description=long_description,
      license="MIT",
      classifiers=classifiers
      )
