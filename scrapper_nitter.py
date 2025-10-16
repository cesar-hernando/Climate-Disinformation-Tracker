"""
Module for scraping data from Nitter using Playwright.
Nitter is a free and open source alternative Twitter front-end focused on privacy.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import csv
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright

class ScraperNitter:
    def __init__(self):
        self.domains = self._get_domains()  # List of available Nitter instances
        self.domain = self.domains[0] if self.domains else "https://nitter.net"
        self.browser = None
        self.context = None
        self.playwright = None


    async def __aenter__(self):
        """Start Playwright and open browser context when entering async block."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=True)
        self.context = await self.browser.new_context()
        return self


    async def __aexit__(self, exc_type, exc, tb):
        """Close browser and stop Playwright on exit (even if error occurs)."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


    def _get_domains(self):
        """Fetch the list of clear web Nitter instances."""

        r = requests.get(
            "https://raw.githubusercontent.com/libredirect/instances/main/data.json"
        )
        if r.ok:
            return r.json()["nitter"]["clearnet"]
        else:
            return None

    def __next_domain(self):
        """Switch to the next available Nitter instance."""
        if self.domains:
            current_index = self.domains.index(self.domain)
            next_index = (current_index + 1) % len(self.domains)
            self.domain = self.domains[next_index]
        else:
            self.domain = "https://nitter.net"

    def _get_search_url(
        self, query, since="", until="", near="", filters={}, excludes={}):
        """Constructs a Nitter search URL based on the given parameters."""

        selectors = [
            "nativeretweets",
            "media",
            "videos",
            "news",
            "verified",
            "native_video",
            "replies",
            "links",
            "images",
            "safe",
            "quote",
            "pro_video",
        ]
        selected = ""
        for s in selectors:
            if s in filters:
                selected += f"&f-{s}=on"
            if s in excludes:
                selected += f"&e-{s}=on" # changed from off to on after seeing how nitter does it

        base_url = "/search?f=tweets&q={query}{selected}&since={since}&until={until}&near={near}" # changed order

        # URL encode parameters
        query = quote_plus(query)
        since = quote_plus(since)
        until = quote_plus(until)
        near = quote_plus(near)
        return base_url.format(
            query=query, since=since, until=until, near=near, selected=selected
        )

    
    async def __fetch_tweets(self, url):
        """Fetch page HTML using Playwright."""

        page = await self.context.new_page()
        full_url = self.domain + url
        try:
            print(f"Fetching URL: {full_url}")
            resp = await page.goto(full_url, timeout=60000, wait_until="domcontentloaded")
            status_code = resp.status if resp else 500
            html = await page.content()
        except Exception as e:
            print(f"Playwright error on {full_url}: {e}")
            html, status_code = "", 500
        finally:
            await page.close()

        return html, status_code


    def __parse_tweets(self, html_content):
        """Parses the HTML content to extract tweet information."""

        def ts_to_iso8601(ts):
            dt = datetime.strptime(ts.replace(" ·", ""), "%b %d, %Y %I:%M %p %Z")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        soup = BeautifulSoup(html_content, "html.parser")
        tweets = []

        if soup.find("h2", class_="timeline-end"):
            return None, "finished"

        for tweet in soup.find_all("div", class_="timeline-item"):
            tweet_data = {}
            username = tweet.find("a", class_="username")
            tweet_data["user"] = username.text.strip() if username else ""

            content = tweet.find("div", class_="tweet-content")
            content = content.text.strip().replace("\n", "\\n") if content else ""
            tweet_data["text"] = f'"{content}"' if content else ""  # Wrap text in quotes to handle commmas in CSV

            timestamp = tweet.find("span", class_="tweet-date")
            tweet_data["created_at_datetime"] = ts_to_iso8601(timestamp.a["title"].strip()) if timestamp and timestamp.a else ""

            link = tweet.find("a", class_="tweet-link")
            tweet_data["link"] = link["href"] if link and link.has_attr("href") else ""

            tweet_stat = tweet.find_all("span", class_="tweet-stat")
            if len(tweet_stat) < 4:
                tweet_data["comments"] = 0
                tweet_data["retweets"] = 0
                tweet_data["quotes"] = 0
                tweet_data["likes"] = 0
            else:
                tweet_data["comments"] = int(tweet_stat[0].div.text.strip().replace(",", "")) if tweet_stat[0].div.text.strip() else 0
                tweet_data["retweets"] = int(tweet_stat[1].div.text.strip().replace(",", "")) if tweet_stat[1].div.text.strip() else 0
                tweet_data["quotes"] = int(tweet_stat[2].div.text.strip().replace(",", "")) if tweet_stat[2].div.text.strip() else 0
                tweet_data["likes"] = int(tweet_stat[3].div.text.strip().replace(",", "")) if tweet_stat[3].div.text.strip() else 0

            tweets.append(tweet_data)

        cursor = None
        show_more = soup.find_all("div", class_="show-more")[-1] if soup.find_all("div", class_="show-more") else None
        if show_more and show_more.a and show_more.a.has_attr("href"):
            href = show_more.a["href"]
            if "&cursor=" in href:
                cursor = '&cursor=' + href.split("&cursor=")[-1]

        return tweets, cursor

    def __save_tweets_to_csv(self, tweets, filename="tweets.csv"):
        """Saves the list of tweets to a CSV file."""

        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "user",
                    "text",
                    "created_at_datetime",
                    "link",
                    "comments",
                    "retweets",
                    "likes",
                    "quotes",
                ],
            )
            if file.tell() == 0:
                writer.writeheader()
            for tweet in tweets:
                writer.writerow(tweet)

    async def get_tweets(self, query, since="", until="", near="", filters={}, excludes={}, save_csv=True, verbose=False, filename=None):
        """
        Retrieves tweets based on the search query and parameters, saving them to a CSV file.
        """

        url = self._get_search_url(query, since, until, near, filters, excludes)
        cursor = ""
        all_tweets = []

        while True:
            if verbose:
                print(f"Fetching tweets from: {self.domain + url + cursor}")
            html_content, status_code = await self.__fetch_tweets(url + cursor)
            if status_code == 200:
                tweets, new_cursor = self.__parse_tweets(html_content)
                all_tweets.extend(tweets if tweets else [])
                if new_cursor == "finished": # No more tweets to fetch
                    return all_tweets
                
                if len(tweets) == 0: # No tweets found on this page, stop the loop
                    self.__next_domain() # Switch to the next domain if no tweets found
                    print(f"No tweets found, switching to next domain: {self.domain}")

                if save_csv:
                    print("Saving tweets to CSV...")
                    self.__save_tweets_to_csv(tweets, filename=filename)
                
                if new_cursor:
                    cursor = new_cursor
            else:
                self.__next_domain() # Switch to the next domain if error occurs
                print(f"Switching to next domain: {self.domain}")
            
    async def check_tweets_exist(self, query, since="", until="", near="", filters={}, excludes={}):
        """Check if there are any tweets matching the search query and parameters."""

        url = self._get_search_url(query, since, until, near, filters, excludes)
        html_content, status_code = await self.__fetch_tweets(url)

        if status_code == 200:
            tweets, _ = self.__parse_tweets(html_content)
            if tweets:
                return True
            else:
                return False
        else:
            return False
            
    async def check_availability(self, all=False):
        """
        Check if the selected Nitter instance is reachable.
        If all=True, check all instances and return a list of their availability.
        """

        if all:
            all_domains = self._get_domains()
            availability_all = []
            for i, domain in enumerate(all_domains):
                try:
                    with async_playwright() as p:
                        browser = await p.firefox.launch(headless=True)
                        page = await browser.new_page()
                        try:
                            ply_resp = await page.goto(domain, timeout=10000, wait_until="domcontentloaded")
                            status = ply_resp.status if ply_resp else 500
                        except Exception:
                            status = 500
                        finally:
                            await browser.close()

                    class _Resp:
                        def __init__(self, status):
                            self.status_code = status

                    response = _Resp(status)
                    availability_all.append(response.status_code == 200)
                except requests.RequestException:
                    availability_all.append(False)
            return availability_all
        else:
            try:
                response = requests.get(self.domain, timeout=10)
                availability = response.status_code == 200
            except requests.RequestException:
                availability = False
            finally:
                return availability
 



if __name__ == "__main__":
    async def main():
        
        claim = "the Earth has always warmed and cooled"
        initial_date = "2023-01-01"
        final_date = "2025-10-01"
        filename = f'test_Earth_warmed_cooled_{initial_date}_to_{final_date}.csv'

        async with ScraperNitter() as scraper:
            await scraper.get_tweets(
                query=claim, 
                since=initial_date, 
                until=final_date, 
                excludes={"nativeretweets", "replies"}, 
                filename=filename)

        print(f"Scraping completed. Tweets saved to {filename}.")

    asyncio.run(main())
