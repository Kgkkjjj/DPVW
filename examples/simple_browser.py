from dpvw import Browser

if __name__ == "__main__":
    # Start the browser with a custom home page and dark mode enabled
    browser = Browser(home_url="https://www.python.org", dark_mode=True, use_cache=False)
    browser.run()
