from setuptools import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="CrystalAspects",
    version="1.1",
    packages=[
        "CrystalAspects.data",
        "CrystalAspects.GUI",
        "CrystalAspects.tools",
        "CrystalAspects.visualisation",
    ],
    install_requires=required,
    url="",
    license="",
    author="Alvin Jenner Walisinghe & Nathan de Bruyn",
    author_email="jennerwalisinghe@gmail.com, nathandebruyn@icloud.com",
    description="Data Processing tool for CrystalGrower software suite",
)
