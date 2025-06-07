# DPVW

DPVW is a small Python framework for creating graphical web browsers
using only modules from the Python standard library.  The `Browser`
class is built on top of `tkinter` and `urllib` and now provides a few
conveniences such as multiple tabs, back/forward navigation and a tiny
in-memory cache.  Additional tools include bookmark and history lists,
opening of local files and viewing page source.  Recent updates add
home and reload buttons, cache clearing and the ability to save pages to
disk, still using only the standard library.  Further tools allow finding
text within a page, stepping through tabs, toggling dark mode and turning
caching on or off.  It is dependency
free so it can
serve as a lightweight starting point for custom browser-like
applications.

The project is intentionally small and dependency free so it can be used
as a starting point for experimenting with custom user interfaces without
requiring external packages.

## Usage

Run the example browser:

```bash
python examples/simple_browser.py
```

This opens a window with an address bar, navigation controls and a
tabbed display area.  Enter a URL and press **Go** to fetch and display
the page contents.  Additional tabs can be opened via the *New Tab*
button.  Pages are stored briefly in memory so visiting the same address
again is faster.  You can bookmark pages, view your history, load HTML
files from disk or inspect the page source from the toolbar buttons.
Reloading the current page, jumping to your home URL, saving the raw
HTML and clearing the cache are also available from the toolbar.  You can
search for text within the current page, cycle through tabs, toggle dark
mode or disable caching at any time.

Other conveniences include buttons to zoom the text in or out and open
the current URL in your system's default browser.  You can also clear
the navigation history with a single click.  The constructor accepts a
``font_size`` option to control the initial text size, and the home page
loads automatically when the window opens.
