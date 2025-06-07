"""DPVW package.

This package provides a small framework for building GUI-based web
browsers using only the Python standard library.  The :class:`Browser`
offers a tabbed window with navigation controls, bookmarking, history
viewing, opening of local files and the ability to display page source.
Additional toolbar buttons allow reloading the current page, jumping to
a configurable home URL, saving pages to disk and clearing the built-in
cache.  Other tools provide in-page searching, tab cycling, a dark mode
toggle and the ability to enable or disable caching, all implemented
using ``tkinter`` and ``urllib`` only.
"""

from .browser import Browser

__all__ = ["Browser"]
