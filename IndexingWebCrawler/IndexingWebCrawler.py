# this is a try-out example from https://dev.to/fprime/how-to-create-a-web-crawler-from-scratch-in-python-2p46
import requests
import re
from urllib.parse import urlparse
import os


class IndexingWebCrawler:
    def __init__(self, starting_url=None):
        self.starting_url = starting_url
        self.visited = set()

        #To get the proxy token, go to proxyorbit.com to create a new account
        # and store the API key in System Environment Variables with name "PROXY_ORBIT_TOKEN"
        self.proxy_orbit_key = os.getenv("PROXY_ORBIT_TOKEN")
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        self.proxy_orbit_url = f"https://api.proxyorbit.com/v1/?token={self.proxy_orbit_key}&ssl=true&rtt=0.3&protocols=http&lastChecked=30"

    def start(self):
        self.crawl(self.starting_url)

    def get_html(self, url):
        try:
            proxy_info = requests.get(self.proxy_orbit_url).json()
            proxy = proxy_info["curl"]
            html = requests.get(url, headers={"User-Agent":self.user_agent}, proxies={"http":proxy, "https":proxy}, timeout=5)
        except Exception as e:
            print(e)
            return ""
        return html.content.decode("latin-1")

    def get_links(self, url):
        html = self.get_html(url)
        parsed = urlparse(url)
        # base net location
        base = f"{parsed.scheme}://{parsed.netloc}"
        # all the links on the current website
        # match strings like <a href="https://about.google/?fg=1&amp;utm_source=google-DE&amp;utm_medium=referral&amp;utm_campaign=hp-header"
        # <a class="gb_g" data-pid="2" href="https://www.google.de/imghp?hl=en&amp;tab=wi&amp;authuser=0&amp;ogbl"
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
        # adjust found links to real url
        for i, link in enumerate(links):
            if not urlparse(link).netloc:
                link_with_base = base + link
                links[i] = link_with_base

        return set(filter(lambda x: 'mailto' not in x, links))

    def extract_info(self, url):
        html = self.get_html(url)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html)
        return dict(meta)

    def crawl(self, url):
        for link in self.get_links(url):
            if link in self.visited:
                continue
            self.visited.add(link)
            info = self.extract_info(link)
            print(f"""Link: {link}
                    Description: {info.get("description")}
                    Keywords: {info.get("keywords")}""")

            self.crawl(link)


if __name__ == "__main__":
    crawler = IndexingWebCrawler("https://google.com")
    crawler.start()
