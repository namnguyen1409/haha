# -*- coding: utf-8 -*-
import logging
import os, json
from natsort import os_sorted
# from time import time
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler
from bs4 import BeautifulSoup
import requests, threading
import re


logger = logging.getLogger(__name__)

lock = threading.Lock()


class WordpressCrawler(Crawler):
    
    base_url = ["https://wordpress.com/"]

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
            if( a.text.strip() and 'wordpress.com' in a['href'] ):
                self.chapters.append(
                    {
                        "id": len(self.chapters) + 1,
                        "title": a.text.strip(),
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def check_passwords(self, url, name_chapter):
        try:
            import requests
        except ImportError:
            os.system('pip install requests')
            import requests
        try:
            from urllib.parse import urlparse
        except ImportError:
            os.system('pip install urllib3')
            from urllib.parse import urlparse

        postlink = f"{urlparse(url).scheme}://{urlparse(url).netloc}/wp-login.php?action=postpass"

        soup = self.get_soup(url)

        if soup.select_one('meta[property="og:title"]') == None:
            lock.acquire()
            soup = self.get_soup(f"http://127.0.0.1:5000/proxy?url={url}")
            lock.release()
        while soup.find("form", {"class": "post-password-form"}):
            # pass2 = TelegramBot.handle_chapter_password(f'Enter the password for {name_chapter}')
            # print(pass2)
            password2 = input(f'Enter the password for {name_chapter}: ')
            s2 = requests.Session()
            login_data = {"post_password": password2, "Submit": "Enter"}
            # self.post_soup(postlink, data=login_data)
            s2.post(postlink, data=login_data)
            r = s2.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            
        return soup

    def download_chapter_body(self, chapter):
        soup = self.check_passwords(chapter["url"], chapter["title"])
        content = ""
        try:
            contents = soup.find("div", {"class": "entry-content"})
        except:
            contents = soup.find("div", {"class": "post-content"})
        try:
            for tag in contents.find_all(lambda tag: tag.has_attr('style') and self.is_hidden_style(tag['style'])):
                # Loại bỏ thẻ
                tag.decompose()
            for i in contents.find_all('p', {"class":"CalendarMonthGrid_month__hideForAnimation"}):
                i.decompose()
            content = BeautifulSoup(contents.prettify(), 'html.parser')
        except:
            pass
        # api_url = "http://127.0.0.1:5000/ocr?language=vie"
        # if len(content.find_all('img')) > 10:
        #     imagesContent = ""
        #     for img in content.find_all('img'):
        #         data = {
        #             "image_url": img['data-orig-file']
        #         }
        #         r = requests.post(api_url, data=data)
        #         imagesContent += self.removeSymbols(r.json()['text'])
        #     return f"<p>{imagesContent.strip()}</p>"
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
        ]
        for regex in hidden_styles_regex:
            if regex.search(style):
                return True
        return False
    
    def removeSymbols(self, string: str) -> str:
        # Chuyển về một dòng nếu có nhiều dòng
        string = string.replace('\n', ' ')
        # Thay đổi nhiều khoảng trắng thành một khoảng trắng giữa 2 từ
        string = ' '.join(string.split())
        return f"{string.strip()} "
