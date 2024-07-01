# -*- coding: utf-8 -*-
import logging
import os, json
from natsort import os_sorted
# from time import time
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler
from bs4 import BeautifulSoup
import threading
import re


logger = logging.getLogger(__name__)


class WordpressCrawler(Crawler):
    
    base_url = ["https://blogspot.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(["Prev", "ToC", "Next"])

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        # No author names listed
        self.novel_author = "-----"
        logger.info("Novel author: %s", self.novel_author)

        try:
            toc_parts = soup.select_one("div.entry-content")
        except:
            toc_parts = soup.select_one("div.post-content")
        for notoc in toc_parts.select(
            ".sharedaddy, .inline-ad-slot, .code-block, script, .adsbygoogle"
        ):
            notoc.extract()
            
        try:
            chapters = soup.select(
                f'div.entry-content a'
            )
        except:
            chapters = soup.select(
                f'div.post-content a'
            )
        for a in chapters:
            if( a.text.strip() and 'blogspot.com' in a['href'] ):
                self.chapters.append(
                    {
                        "id": len(self.chapters) + 1,
                        "title": a.text.strip(),
                        "url": self.absolute_url(a["href"]),
                    }
                )


    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        try:
            contents = soup.find("div", {"class": "entry-content"})
        except:
            contents = soup.find("div", {"class": "post-content"})
        try:
            for tag in contents.find_all(lambda tag: tag.has_attr('style') and self.is_hidden_style(tag['style'])):
                # Loại bỏ thẻ
                tag.decompose()

            content = BeautifulSoup(contents.prettify(), 'html.parser')
        except:
            pass
        return self.cleaner.extract_contents(content)
    


    def is_hidden_style(self, style):
        # Define regular expressions for hidden styles
        hidden_styles_regex = [
            re.compile(r"opacity:\s*0", re.IGNORECASE),
            re.compile(r"font-size:\s*0*\.?0+px", re.IGNORECASE),
            re.compile(r"line-height:\s*0*\.?0+px", re.IGNORECASE),
            re.compile(r"line-height:\s*calc\([^)]+1px/\d{3}\)", re.IGNORECASE),
            re.compile(r"visibility:\s*hidden", re.IGNORECASE),
            re.compile(r"display:\s*none", re.IGNORECASE),
            re.compile(r"color:\s*rgba?\(?\s*0\s*,\s*0\s*,\s*0\s*(?:,\s*0\s*)?\)", re.IGNORECASE),
            # style="color: white;" is also a hidden style
            re.compile(r"color:\s*white", re.IGNORECASE),
            re.compile(r"color:\s*", re.IGNORECASE),
        ]
        for regex in hidden_styles_regex:
            if regex.search(style):
                return True
        return False