"""Simple web browser framework using only the Python standard library.

This module defines a ``Browser`` class with multiple tabs, navigation
history and bookmarking.  It also provides utilities for viewing page
source, loading local files, reloading pages, navigating to a home URL
and saving content.  Everything is implemented using only modules from
the Python standard library.
"""

from tkinter import (
    Tk,
    Entry,
    Button,
    Text,
    Scrollbar,
    Listbox,
    Toplevel,
    END,
    RIGHT,
    LEFT,
    Y,
    X,
    BOTTOM,
    Frame,
    Label,
    filedialog,
    font as tkfont,
)
from tkinter.ttk import Notebook
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import webbrowser


class History:
    """Simple navigation history tracker."""

    def __init__(self) -> None:
        self._entries: list[str] = []
        self._index = -1

    def add(self, url: str) -> None:
        if self._index < len(self._entries) - 1:
            self._entries = self._entries[: self._index + 1]
        self._entries.append(url)
        self._index = len(self._entries) - 1

    def back(self) -> str | None:
        if self._index > 0:
            self._index -= 1
            return self._entries[self._index]
        return None

    def forward(self) -> str | None:
        if self._index < len(self._entries) - 1:
            self._index += 1
            return self._entries[self._index]
        return None

    def clear(self) -> None:
        """Remove all entries from the history."""
        self._entries.clear()
        self._index = -1


class BookmarkManager:
    """Minimal list of bookmarked URLs."""

    def __init__(self) -> None:
        self.bookmarks: list[str] = []

    def add(self, url: str) -> None:
        if url not in self.bookmarks:
            self.bookmarks.append(url)

    def remove(self, url: str) -> None:
        if url in self.bookmarks:
            self.bookmarks.remove(url)


class _Cache:
    """Very small in-memory cache of pages."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, url: str) -> str | None:
        return self._data.get(url)

    def set(self, url: str, html: str) -> None:
        self._data[url] = html

    def clear(self) -> None:
        self._data.clear()


class _HTMLTextParser(HTMLParser):
    """Convert raw HTML into plain text for display."""

    def __init__(self):
        super().__init__()
        self._text = []

    def handle_data(self, data: str) -> None:
        self._text.append(data)

    def text(self) -> str:
        return "".join(self._text)


def _fetch_url(url: str) -> str:
    """Fetch ``url`` and return its HTML body as text."""
    try:
        with urlopen(url) as response:
            encoding = response.headers.get_content_charset("utf-8")
            return response.read().decode(encoding)
    except HTTPError as exc:
        return f"HTTP error: {exc.code}"
    except URLError as exc:
        return f"URL error: {exc.reason}"


class BrowserTab:
    """Represents a single tab within the ``Browser`` window."""

    def __init__(self, notebook: Notebook, font: tkfont.Font, title: str = "Tab") -> None:
        self.frame = Frame(notebook)
        self.display = Text(self.frame, wrap="word", font=font)
        self.scroll = Scrollbar(self.frame, command=self.display.yview)
        self.display.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.display.pack(side=LEFT, fill="both", expand=True)
        notebook.add(self.frame, text=title)

    def show_text(self, text: str) -> None:
        self.display.delete("1.0", END)
        self.display.insert("1.0", text)


class Browser:
    """A basic multi-tab browser based on ``tkinter``."""

    def __init__(
        self,
        title: str = "DPVW Browser",
        home_url: str = "https://example.com",
        *,
        use_cache: bool = True,
        dark_mode: bool = False,
        font_size: int = 12,
    ) -> None:
        self.root = Tk()
        self.root.title(title)

        self.font = tkfont.Font(size=font_size)

        self.home_url = home_url

        self.history = History()
        self.bookmarks = BookmarkManager()
        self.cache = _Cache()
        self.use_cache = use_cache
        self.dark_mode = dark_mode

        control_bar = Frame(self.root)
        control_bar.pack(side="top", fill=X)

        self.back_button = Button(control_bar, text="Back", command=self.go_back)
        self.back_button.pack(side=LEFT)

        self.forward_button = Button(control_bar, text="Forward", command=self.go_forward)
        self.forward_button.pack(side=LEFT)

        self.address = Entry(control_bar, width=50)
        self.address.pack(side=LEFT, fill=X, expand=True)

        self.go_button = Button(control_bar, text="Go", command=self.open_url)
        self.go_button.pack(side=LEFT)

        self.new_tab_button = Button(control_bar, text="New Tab", command=self.new_tab)
        self.new_tab_button.pack(side=LEFT)

        self.add_bookmark_button = Button(control_bar, text="Add Bookmark", command=self.add_bookmark)
        self.add_bookmark_button.pack(side=LEFT)

        self.show_bookmarks_button = Button(control_bar, text="Bookmarks", command=self.show_bookmarks)
        self.show_bookmarks_button.pack(side=LEFT)

        self.history_button = Button(control_bar, text="History", command=self.show_history)
        self.history_button.pack(side=LEFT)

        self.view_source_button = Button(control_bar, text="View Source", command=self.view_source)
        self.view_source_button.pack(side=LEFT)

        self.open_file_button = Button(control_bar, text="Open File", command=self.open_file)
        self.open_file_button.pack(side=LEFT)

        self.find_button = Button(control_bar, text="Find", command=self.find_text)
        self.find_button.pack(side=LEFT)

        self.prev_tab_button = Button(control_bar, text="Prev Tab", command=self.prev_tab)
        self.prev_tab_button.pack(side=LEFT)

        self.next_tab_button = Button(control_bar, text="Next Tab", command=self.next_tab)
        self.next_tab_button.pack(side=LEFT)

        self.reload_button = Button(control_bar, text="Reload", command=self.reload_page)
        self.reload_button.pack(side=LEFT)

        self.home_button = Button(control_bar, text="Home", command=self.go_home)
        self.home_button.pack(side=LEFT)

        self.save_button = Button(control_bar, text="Save", command=self.save_page)
        self.save_button.pack(side=LEFT)

        self.clear_cache_button = Button(control_bar, text="Clear Cache", command=self.clear_cache)
        self.clear_cache_button.pack(side=LEFT)

        self.cache_toggle_button = Button(control_bar, text="Disable Cache", command=self.toggle_cache)
        self.cache_toggle_button.pack(side=LEFT)

        self.dark_mode_button = Button(control_bar, text="Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side=LEFT)

        self.zoom_in_button = Button(control_bar, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side=LEFT)

        self.zoom_out_button = Button(control_bar, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side=LEFT)

        self.external_button = Button(control_bar, text="Open External", command=self.open_external)
        self.external_button.pack(side=LEFT)

        self.clear_history_button = Button(control_bar, text="Clear History", command=self.clear_history)
        self.clear_history_button.pack(side=LEFT)

        self.notebook = Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.tabs: list[BrowserTab] = []
        self.new_tab()
        self.go_home()

        self.status = Label(self.root, text="Ready")
        self.status.pack(side=BOTTOM, fill=X)

    def current_tab(self) -> BrowserTab:
        index = self.notebook.index("current")
        return self.tabs[index]

    def new_tab(self) -> None:
        tab = BrowserTab(self.notebook, self.font, title=f"Tab {len(self.tabs)+1}")
        if self.dark_mode:
            tab.display.config(background="#2e2e2e", foreground="#dcdcdc")
        self.tabs.append(tab)
        self.notebook.select(len(self.tabs) - 1)

    def _display_text(self, text: str) -> None:
        self.current_tab().show_text(text)

    def open_url(self, url: str | None = None) -> None:
        if url is None:
            url = self.address.get()
        self.status.config(text=f"Loading {url}...")
        cached = self.cache.get(url) if self.use_cache else None
        if cached is None:
            html = _fetch_url(url)
            if self.use_cache:
                self.cache.set(url, html)
        else:
            html = cached
        parser = _HTMLTextParser()
        parser.feed(html)
        self._display_text(parser.text())
        self.history.add(url)
        self.status.config(text=url)

    def go_back(self) -> None:
        url = self.history.back()
        if url:
            self.address.delete(0, END)
            self.address.insert(0, url)
            self.open_url(url)

    def go_forward(self) -> None:
        url = self.history.forward()
        if url:
            self.address.delete(0, END)
            self.address.insert(0, url)
            self.open_url(url)

    def add_bookmark(self) -> None:
        url = self.address.get()
        if url:
            self.bookmarks.add(url)
            self.status.config(text=f"Bookmarked {url}")

    def _show_list_window(self, title: str, items: list[str]) -> None:
        window = Toplevel(self.root)
        window.title(title)
        listbox = Listbox(window)
        scrollbar = Scrollbar(window, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        for item in items:
            listbox.insert(END, item)
        listbox.pack(side=LEFT, fill="both", expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        def load_selected(_: object = None) -> None:
            selection = listbox.curselection()
            if selection:
                url = listbox.get(selection[0])
                self.address.delete(0, END)
                self.address.insert(0, url)
                self.open_url(url)
                window.destroy()

        listbox.bind("<Double-Button-1>", load_selected)
        Button(window, text="Open", command=load_selected).pack(side=BOTTOM)

    def show_bookmarks(self) -> None:
        self._show_list_window("Bookmarks", self.bookmarks.bookmarks)

    def show_history(self) -> None:
        self._show_list_window("History", self.history._entries)

    def view_source(self) -> None:
        url = self.address.get()
        cached = self.cache.get(url) if self.use_cache else None
        if cached is None:
            html = _fetch_url(url)
            if self.use_cache:
                self.cache.set(url, html)
        else:
            html = cached
        tab = BrowserTab(self.notebook, self.font, title="Source")
        self.tabs.append(tab)
        tab.show_text(html)
        self.notebook.select(len(self.tabs) - 1)

    def open_file(self) -> None:
        filename = filedialog.askopenfilename(filetypes=[("HTML files", "*.html"), ("All files", "*.*")])
        if filename:
            with open(filename, "r", encoding="utf-8", errors="ignore") as fh:
                html = fh.read()
            tab = BrowserTab(self.notebook, self.font, title=filename)
            self.tabs.append(tab)
            parser = _HTMLTextParser()
            parser.feed(html)
            tab.show_text(parser.text())
            self.notebook.select(len(self.tabs) - 1)

    def reload_page(self) -> None:
        url = self.address.get()
        if url:
            html = _fetch_url(url)
            if self.use_cache:
                self.cache.set(url, html)
            self.open_url(url)

    def go_home(self) -> None:
        self.address.delete(0, END)
        self.address.insert(0, self.home_url)
        self.open_url(self.home_url)

    def save_page(self) -> None:
        url = self.address.get()
        if not url:
            return
        cached = self.cache.get(url) if self.use_cache else None
        if cached is None:
            html = _fetch_url(url)
            if self.use_cache:
                self.cache.set(url, html)
        else:
            html = cached
        filename = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html"), ("All files", "*.*")])
        if filename:
            with open(filename, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write(html)
            self.status.config(text=f"Saved to {filename}")

    def clear_cache(self) -> None:
        self.cache.clear()
        self.status.config(text="Cache cleared")

    def clear_history(self) -> None:
        self.history.clear()
        self.status.config(text="History cleared")

    def toggle_cache(self) -> None:
        self.use_cache = not self.use_cache
        state = "enabled" if self.use_cache else "disabled"
        self.cache_toggle_button.config(text=("Disable Cache" if self.use_cache else "Enable Cache"))
        if not self.use_cache:
            self.cache.clear()
        self.status.config(text=f"Cache {state}")

    def prev_tab(self) -> None:
        index = self.notebook.index("current")
        if index > 0:
            self.notebook.select(index - 1)

    def next_tab(self) -> None:
        index = self.notebook.index("current")
        if index < len(self.tabs) - 1:
            self.notebook.select(index + 1)

    def find_text(self) -> None:
        window = Toplevel(self.root)
        window.title("Find")
        entry = Entry(window)
        entry.pack(side=LEFT, fill=X, expand=True)

        def do_find() -> None:
            term = entry.get()
            text_widget = self.current_tab().display
            text_widget.tag_remove("highlight", "1.0", END)
            if term:
                idx = text_widget.search(term, "1.0", END)
                if idx:
                    end = f"{idx}+{len(term)}c"
                    text_widget.tag_add("highlight", idx, end)
                    text_widget.tag_config("highlight", background="yellow")

        Button(window, text="Find", command=do_find).pack(side=LEFT)

    def toggle_dark_mode(self) -> None:
        self.dark_mode = not self.dark_mode
        bg = "#2e2e2e" if self.dark_mode else "white"
        fg = "#dcdcdc" if self.dark_mode else "black"
        for tab in self.tabs:
            tab.display.config(background=bg, foreground=fg)
        self.root.config(background=bg)
        self.address.config(background=bg, foreground=fg, insertbackground=fg)
        self.status.config(background=bg, foreground=fg)
        state = "enabled" if self.dark_mode else "disabled"
        self.dark_mode_button.config(text=("Light Mode" if self.dark_mode else "Dark Mode"))
        self.status.config(text=f"Dark mode {state}")

    def zoom_in(self) -> None:
        size = self.font["size"] + 2
        self.font.configure(size=size)
        self.status.config(text=f"Zoom {size}")

    def zoom_out(self) -> None:
        size = max(6, self.font["size"] - 2)
        self.font.configure(size=size)
        self.status.config(text=f"Zoom {size}")

    def open_external(self) -> None:
        url = self.address.get()
        if url:
            webbrowser.open(url)
            self.status.config(text=f"Opened {url} externally")

    def run(self) -> None:
        self.root.mainloop()
