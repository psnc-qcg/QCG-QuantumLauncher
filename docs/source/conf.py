import sys
from pathlib import Path
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.abspath('..'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Quantum Launcher'
copyright = '2024, Dawid Siera'
author = 'Dawid Siera'
release = '1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'autoapi.extension',
]

templates_path = ['_templates']
exclude_patterns = []
autoapi_dirs = ['../../quantum_launcher']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'ansys_sphinx_theme'
html_static_path = ['_static']
html_theme_options = {
    "logo": {
        "image_light": "_static/logo.png",
        "image_dark": "_static/logo.png",
    }
}

html_sidebars = {
    "usage": [],
    "contribution": [],
}
