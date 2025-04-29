import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urljoin, urlparse
import re
import time
from collections import deque

def can_fetch(url, user_agent='MyWebCrawler'):
    """
    Checks if the crawler is allowed to access a given URL based on the site's robots.txt.

    Args:
        url (str): The URL to check.
        user_agent (str, optional): The user agent string to use. Defaults to 'MyWebCrawler'.

    Returns:
        bool: True if the URL can be fetched, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = urljoin(base_url, 'robots.txt')

        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()  # Read the robots.txt file

        return rp.can_fetch(user_agent, url)
    except Exception as e:
        print(f"Error checking robots.txt for {url}: {e}")
        return True # Default to allowing if robots.txt is inaccessible or malformed.  Be conservative.

def extract_text(soup):
    """
    Extracts the main text content from a BeautifulSoup object, discarding HTML tags.

    Args:
        soup (BeautifulSoup): The parsed HTML content.

    Returns:
        str: The extracted text, with whitespace normalized.
    """
    # Remove script and style elements
    for script_or_style in soup.find_all(['script', 'style']):
        script_or_style.decompose()

    # Get the text but keep newlines
    text = soup.get_text(separator="\n")

    # Replace multiple newlines with single newlines, and remove leading/trailing whitespace
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def get_title(soup):
    """
    Extracts the title of the webpage.

    Args:
        soup (BeautifulSoup): The parsed HTML content.

    Returns:
        str: The title of the page, or "No Title Found" if not present.
    """
    title_tag = soup.find('title')
    return title_tag.text.strip() if title_tag else "No Title Found"

def get_links(soup, base_url):
    """
    Extracts all valid and crawlable links from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The parsed HTML content.
        base_url (str): The base URL of the page being scraped.

    Returns:
        list: A list of absolute URLs.
    """
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Make the URL absolute
        absolute_url = urljoin(base_url, href)
        # basic URL validation and filtering.
        if absolute_url.startswith(('http://', 'https://')):
           links.append(absolute_url)
    return links

def crawl(start_url, max_depth=1, max_pages=100, user_agent='MyWebCrawler', obey_robots=True):
    """
    Crawls a website starting from a given URL, respecting robots.txt and handling errors.

    Args:
        start_url (str): The URL to start the crawl from.
        max_depth (int, optional): The maximum depth to crawl. Defaults to 1.
        max_pages (int, optional): The maximum number of pages to crawl. Defaults to 100.
        user_agent (str, optional): The user agent string to use. Defaults to 'MyWebCrawler'.
        obey_robots (bool, optional): Whether to obey robots.txt. Defaults to True.

    Returns:
        dict: A dictionary where keys are URLs and values are dictionaries
              containing 'title', 'text', and 'links'.
              Returns None on critical error.
    """
    crawled = {}
    to_crawl = deque([(start_url, 0)])  # Use a deque for BFS, store (url, depth)
    pages_crawled = 0

    if obey_robots and not can_fetch(start_url, user_agent):
        print(f"[{user_agent}] Cannot crawl {start_url} due to robots.txt.")
        return {}  # Return empty dict to indicate no pages crawled

    try:
        while to_crawl and pages_crawled < max_pages:
            current_url, depth = to_crawl.popleft()

            if current_url in crawled:
                continue  # Skip if already crawled

            if depth > max_depth:
                print(f"Skipping {current_url} due to max depth ({max_depth}) reached.")
                continue

            if obey_robots and not can_fetch(current_url, user_agent):
                print(f"[{user_agent}] Cannot crawl {current_url} due to robots.txt.")
                continue

            try:
                print(f"[{user_agent}] Crawling: {current_url} (Depth: {depth})")
                response = requests.get(current_url, headers={'User-Agent': user_agent}, timeout=10) #set a timeout
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                soup = BeautifulSoup(response.content, 'html.parser')

                title = get_title(soup)
                text = extract_text(soup)
                links = get_links(soup, current_url)

                crawled[current_url] = {
                    'title': title,
                    'text': text,
                    'links': links,
                }
                pages_crawled += 1

                # Add new links to the queue
                for link in links:
                    if link not in crawled:
                        to_crawl.append((link, depth + 1))

                time.sleep(0.1) # be nice and slow
            except requests.exceptions.RequestException as e:
                print(f"[{user_agent}] Error fetching {current_url}: {e}")
            except Exception as e:
                print(f"[{user_agent}] Error processing {current_url}: {e}")
        return crawled
    except Exception as e:
        print(f"[{user_agent}] A critical error occurred: {e}")
        return None  # Return None for a critical error

if __name__ == '__main__':
#    start_url = 'https://grapeandgrind.co.uk'#'https://www.example.com'  # Replace with the URL you want to crawl
    start_url = 'https://grapeandgrind.co.uk/shop/?fwp_categories=red'
    max_depth = 1#2
    max_pages = 1#50
    user_agent = 'someone' #change user agent
    obey_robots = True # added obey robots

    data = crawl(start_url, max_depth, max_pages, user_agent, obey_robots)

    if data:
        print(f"Successfully crawled {len(data)} pages.")
        # You can now process the 'data' dictionary as needed.  For example, print the titles and URLs:
        for url, content in data.items():
            print(f"URL: {url}")
            print(f"Title: {content['title']}")
            print("-" * 20)
            print(f"Text: {content['text']}")
            with open(f"{urlparse(url).netloc}.txt", "w", encoding="utf-8") as f:
                f.write(content['text'])
    else:
        print("Crawl failed.")