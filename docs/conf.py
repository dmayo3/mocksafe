project = "mocksafe"

release = "0.1"
version = "0.1.0"

extensions = [
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

html_theme = "sphinx_rtd_theme"


def skip(app, what, name, obj, skip, options):
    if name == "__setattr__":
        return skip
    if name.startswith("_"):
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)


autodoc_default_options = {
    "undoc-members": False,
}


doctest_global_setup = """
from random import Random
from mocksafe import MockProperty, mock, mock_module, stub, when, that, spy
mock_random: Random = mock(Random)
"""
