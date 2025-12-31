# docs/conf.py
import os
import sys
from datetime import datetime

# 1. Rutas de código
# Apuntamos a ../src para que Sphinx encuentre el paquete pygeko
sys.path.insert(0, os.path.abspath('../src'))

# 2. Información del proyecto
project = 'pyGEKO'
copyright = f'{datetime.now().year}, Jesús Cabrera'
author = 'Jesús Cabrera'
release = '0.1.0'

# 3. Extensiones principales
extensions = [
    'sphinx.ext.autodoc',      # Genera documentación de docstrings
    'sphinx.ext.viewcode',     # Añade enlaces al código fuente
    'sphinx.ext.napoleon',     # Soporta formato Google/NumPy docstrings
    'sphinx.ext.intersphinx',  # Enlaza a docs oficiales de numpy, pandas, etc.
    'sphinx_autodoc_typehints', # Extrae tipos de las firmas de funciones
    'sphinx.ext.githubpages',  # Útil para hosting en GitHub Pages
]

# 4. Configuración de InterSphinx
# Esto permite que si usas np.ndarray en un tipo, sea un enlace a la web de NumPy
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# 5. Opciones de Autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# 6. Interfaz (Tema)
# Usamos el estándar de ReadTheDocs
html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

# Opcional: Logo del proyecto (si tienes uno en _static/logo.png)
# html_logo = "_static/logo.png"

# 7. Configuración de idioma
language = 'en'