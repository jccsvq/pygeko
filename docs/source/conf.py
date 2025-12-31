# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path
from datetime import datetime

from pygeko.__about__ import __version__ as VERSION

sys.path.insert(0, str(Path('../../src').resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyGEKO'
copyright = f'{datetime.now().year}, Jesús Cabrera'
author = 'jccsvq@gmail.com'
release = VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
   'sphinx.ext.duration',
   'sphinx.ext.doctest',
   'sphinx.ext.autodoc',
   'sphinx.ext.autosummary',
   'sphinx.ext.mathjax',
   'sphinx_book_theme',
   'myst_parser',
   'sphinx.ext.napoleon',   # Ya incluido en Sphinx
   'sphinx_autodoc_typehints', # Instalado vía pip

]

templates_path = ['_templates']
exclude_patterns = []

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
# Permite que autodoc vea miembros privados
autodoc_default_options = {
    'private-members': True,
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ['_static']
html_logo = '_static/pyGEKO_logo.png'
html_favicon = '_static/favicon.png'



