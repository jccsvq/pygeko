# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

# 1. Asegúrate de que Sphinx pueda encontrar tu código
sys.path.insert(0, os.path.abspath("../../src"))

# 2. Importa la versión desde tu archivo de metadatos
# Importamos así para no tener que instalar el paquete durante la compilación de la docu
about = {}
with open(os.path.abspath("../../src/pygeko/__about__.py")) as f:
    exec(f.read(), about)

project = "pyGEKO"
copyright = f"{datetime.now().year}, Jesús Cabrera"
author = "jccsvq@gmail.com"

# 3. Usa los valores extraídos
release = about["__version__"]  # Ejemplo: '0.9.0rc1'
version = ".".join(release.split(".")[:2])  # Extrae '0.9' automáticamente

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx_math_dollar",
    "sphinx_book_theme",
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "amsmath",
    "dollarmath",
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
# Permite que autodoc vea miembros privados
autodoc_default_options = {
    "private-members": True,
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "_static/pyGEKO_logo.png"
html_favicon = "_static/favicon.png"

# For copybutton
#copybutton_exclude = '--> '