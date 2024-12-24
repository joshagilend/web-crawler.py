import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re

class WebCrawler:
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque([base_url])
        self.emails = set()

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def extract_links(self, soup, current_url):
        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(current_url, href)
            if self.is_valid_url(full_url) and full_url not in self.visited:
                links.add(full_url)
        return links

    def extract_emails(self, text):
        self.emails.update(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))

    def crawl(self):
        pages_crawled = 0

        while self.queue and pages_crawled < self.max_pages:
            current_url = self.queue.popleft()

            if current_url in self.visited:
                continue

            print(f"Crawling: {current_url}")
            self.visited.add(current_url)
            try:
                response = requests.get(current_url, timeout=5)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                self.extract_emails(response.text)
                links = self.extract_links(soup, current_url)

                self.queue.extend(links)
                pages_crawled += 1
            except requests.RequestException as e:
                print(f"Failed to crawl {current_url}: {e}")

    def save_results(self, output_file="results.txt"):
        with open(output_file, "w") as file:
            file.write("Emails found:\n")
            for email in sorted(self.emails):
                file.write(f"{email}\n")
            file.write("\nVisited URLs:\n")
            for url in sorted(self.visited):
                file.write(f"{url}\n")

if __name__ == "__main__":
    # Change base_url to your target URL
    base_url = "https://example.com"
    crawler = WebCrawler(base_url, max_pages=50)
    crawler.crawl()
    crawler.save_results()
    print("Crawling complete. Results saved in 'results.txt'.")
