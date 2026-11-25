# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import bsutennis

project = 'BsuTennis'
copyright = '2025, Jiangyan Yang'
author = 'Jiangyan Yang'
release = bsutennis.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_togglebutton",
    "sphinx_copybutton",
    "myst_nb",
    "sphinx_thebe",
    "sphinx_comments",
    "sphinx_external_toc",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_book_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_multitoc_numbering",
]

exclude_patterns = ["_build", "**.ipynb_checkpoints", ".DS_Store", "Thumbs.db"]
add_module_names = False
numfig = True

templates_path = ['_templates']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_book_theme"
html_logo = "_static/Logo.png"          
html_favicon = "_static/favicon.ico"
html_title = "BsuTennis Documentation"

html_theme_options = {
    "search_bar_text": "Search this book...",
    "repository_url": "https://github.com/ouyang1030/BsuTennis",  
    "repository_branch": "master",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "home_page_in_toc": True,
    "extra_footer": "<p>BsuTennis: Tennis Court Plot and Data Analysis</p>",
}

html_static_path = ["_static"]

# -- MyST & Notebook settings ------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "linkify",
    "substitution",
    "tasklist",
]
nb_execution_mode = "auto"
nb_execution_timeout = 120