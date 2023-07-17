import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import logging
import random
import concurrent.futures
import tkinter as tk
import tkinter.filedialog
from tkinter import messagebox
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from queue import Queue
import threading
import csv
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class WebScraper:
    def __init__(self, gui, proxies=None, user_agent=None, parser="html.parser"):
        self.gui = gui
        self.queue = Queue()
        self.proxies = proxies
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        self.parser = parser

    def scrape_website(self, url):
        try:
            headers = {'User-Agent': self.user_agent}
            session = requests.Session()
            session.headers.update(headers)

            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('http://', HTTPAdapter(max_retries=retries))

            response = session.get(url, proxies=self.proxies)

            response.raise_for_status()

            # Rendering Javascript if needed
            if self.parser == 'html.parser':
                soup = BeautifulSoup(response.text, self.parser)
            else:
                options = Options()
                options.headless = True
                driver = webdriver.Chrome(chrome_options=options)
                driver.get(url)
                html = driver.page_source
                soup = BeautifulSoup(html, self.parser)

            data = self.extract_data(soup)

            logging.info(data)
            
            self.gui.add_data(data)

            return data

        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while scraping {url}: {e}")
            return None

    def extract_data(self, soup):
        data = soup.prettify()
        return data

    def add_to_queue(self, url):
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            self.queue.put(url)
        else:
            print(f"Invalid URL: {url}")
            
    def start_scraping(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while not self.queue.empty():
                url = self.queue.get()
                executor.submit(self.scrape_website, url)

class GUI:
    def __init__(self, root):
        self.root = root
        self.scraper = WebScraper(self)

        # Set up GUI
        self.entry = tk.Entry(root)
        self.entry.pack()
        self.button = tk.Button(root, text='Scrape', command=self.scrape)
        self.button.pack()
        self.export_button = tk.Button(root, text='Export to CSV', command=self.export)
        self.export_button.pack()
        self.text = tk.Text(root)
        self.text.pack()

    def scrape(self):
        url = self.entry.get()
        if self.validate_url(url):
            self.scraper.add_to_queue(url)
            self.scraper.start_scraping()
        else:
            messagebox.showwarning("Invalid URL", "Please enter a valid URL.")

    def add_data(self, data):
        self.text.insert('end', data)

    def export(self):
        filename = tkinter.filedialog.asksaveasfilename(defaultextension=".csv")
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.text.get(1.0, 'end-1c').splitlines())

    def validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

if __name__ == "__main__":
    logging.basicConfig(filename='scraper.log', level=logging.INFO)

    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
