import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    Function to scrape data from a website.
    Args:
        url (str): The URL of the website to be scraped.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace this with actual scraping code
    print(soup.prettify())

if __name__ == "__main__":
    url = "http://example.com"  # Replace with the website you want to scrape
    scrape_website(url)
