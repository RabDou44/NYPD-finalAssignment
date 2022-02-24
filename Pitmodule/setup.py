from gettext import install
from setuptools import setup

setup(
    name="Pitmodule",
    version="1.0",
    author="Adam Domoslawski",
    py_modules=["pitmodule"],
    install_requires = ['pandas','numpy','openpyxl','xlrd','typing'],
    test_requires = ['pytest']
)
