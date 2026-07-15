# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

#for Build the .EXE file
setup(
    name="sistema 28 de octubre",
    version="1.1",
    description="sistema Informativo para gestion de procesos",
    author="Efren Eduardo Martinez Quijada",
    author_email="xhelax22@gmail.com",
    url="....",
    license="Open Source",
    scripts=["modulo_main.py"],
    console=["modulo_main.py"],
    options={"py2exe": {"bundle_files": 1}},
    zipfile=None,
)
