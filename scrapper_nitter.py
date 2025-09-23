"""
Module for scraping data from Nitter using Playwright.
Nitter is a free and open source alternative Twitter front-end focused on privacy.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import csv
from playwright.sync_api import sync_playwright


class ScraperNitter:
    def __init__(self):
        self.domains = self._get_domains()
        self.domain = self.domains[0] if self.domains else "https://nitter.net"

    def __get_search_url(
        self, query, since="", until="", near="", filters={}, excludes={}
    ):
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
                selected += f"&e-{s}=off"

        base_url = "/search?f=tweets&q={query}&since={since}&until={until}&near={near}{selected}"

        # URL encode parameters
        query = quote_plus(query)
        since = quote_plus(since)
        until = quote_plus(until)
        near = quote_plus(near)
        return base_url.format(
            query=query, since=since, until=until, near=near, selected=selected
        )

    def _get_domains(self):
        """Fetch the list of clear web Nitter instances."""
        r = requests.get(
            "https://raw.githubusercontent.com/libredirect/instances/main/data.json"
        )
        if r.ok:
            return r.json()["nitter"]["clearnet"]
        else:
            return None

    def __fetch_tweets(self, url):
        """Fetch page HTML using Playwright."""

        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            full_url = self.domain + url
            try:
                page.goto(full_url, timeout=30000, wait_until="networkidle")
                html = page.content()
                status_code = 200
            except Exception as e:
                print(f"Playwright error on {full_url}: {e}")
                html, status_code = "", 500
            browser.close()

        return html, status_code

    def __parse_tweets(self, html_content):
        """Parses the HTML content to extract tweet information."""
        soup = BeautifulSoup(html_content, "html.parser")
        tweets = []

        if soup.find("h2", class_="timeline-end"):
            return None, "finished"

        for tweet in soup.find_all("div", class_="timeline-item"):
            tweet_data = {}
            username = tweet.find("a", class_="username")
            tweet_data["username"] = username.text.strip() if username else ""

            content = tweet.find("div", class_="tweet-content")
            content = content.text.strip().replace("\n", " ").replace(",", "&#44;") if content else ""
            tweet_data["content"] = content if content else ""

            timestamp = tweet.find("span", class_="tweet-date")
            tweet_data["timestamp"] = timestamp.a["title"].strip() if timestamp and timestamp.a else ""

            link = tweet.find("a", class_="tweet-link")
            tweet_data["link"] = link["href"] if link and link.has_attr("href") else ""

            tweet_stat = tweet.find_all("span", class_="tweet-stat")
            if len(tweet_stat) < 4:
                tweet_data["comments"] = "0"
                tweet_data["retweets"] = "0"
                tweet_data["quotes"] = "0"
                tweet_data["likes"] = "0"
            else:
                tweet_data["comments"] = tweet_stat[0].div.text.strip() if tweet_stat[0].div.text.strip() else "0"
                tweet_data["retweets"] = tweet_stat[1].div.text.strip() if tweet_stat[1].div.text.strip() else "0"
                tweet_data["quotes"] = tweet_stat[2].div.text.strip() if tweet_stat[2].div.text.strip() else "0"
                tweet_data["likes"] = tweet_stat[3].div.text.strip() if tweet_stat[3].div.text.strip() else "0"

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
                    "username",
                    "content",
                    "timestamp",
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

    def get_tweets(self, query, since="", until="", near="", filters={}, excludes={}):
        url = self.__get_search_url(query, since, until, near, filters, excludes)
        cursor = ""
        while True:
            print(f"Fetching tweets from: {self.domain + url + cursor}")
            html_content, status_code = self.__fetch_tweets(url + cursor)
            if status_code == 200:
                tweets, new_cursor = self.__parse_tweets(html_content)
                if new_cursor == "finished": # No more tweets to fetch
                    print("No more tweets available.")
                    break
                if not tweets:
                    self.domain = self.domains[
                        (self.domains.index(self.domain) + 1) % len(self.domains)
                    ]
                    print(
                        f"No tweets found or bot detection, switching domain to {self.domain}"
                    )
                    continue
                self.__save_tweets_to_csv(tweets)
                
                if new_cursor:
                    cursor = new_cursor

            else:
                print(f"Error {status_code} from {self.domain}, switching domain.")
                self.domain = self.domains[
                    (self.domains.index(self.domain) + 1) % len(self.domains)
                ]


if __name__ == "__main__":
    scraper = ScraperNitter()
    scraper.get_tweets("'climate' AND 'change'", excludes={"nativeretweets", "replies"})
    print("Scraping completed. Tweets saved to tweets.csv.")
