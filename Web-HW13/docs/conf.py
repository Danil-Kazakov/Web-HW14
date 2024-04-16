import sys
import os

sys.path.append(os.path.abspath(('..')))
project = 'HW14'
copyright = '2024, Danil Kazakov'
author = 'Danil Kazakov'


extensions = ["sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


html_theme = 'alabaster'
html_static_path = ['_static']
