# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

from utils import update_proxy, parse_date

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
RADIO_PAGE_URL = "https://www.svoboda.org/news?p=%s"
NEW_PAGE_URL = "news_detail.asp?id="
RADIO_URL = "https://www.svoboda.org"


def parsing_radio_url(page, limit_date, proxy, body):
    try:
        res = requests.get(RADIO_PAGE_URL % page, headers={
            "user-agent": USER_AGENT
        })
    except Exception:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)
    if res.ok:
        soup = BeautifulSoup(res.text)
        tables = soup.find_all("div", {"class": "media-block"})
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:
            try:
                article_date = parse_date(table.find("span", {"class": re.compile("^date date")}).text, "%d %m %Y")
                if article_date >= limit_date:
                    href = table.find("a", {"href": re.compile("^/a/")}).attrs["href"]
                    body.append({"date": article_date, "href": href})
                else:
                    return False, body, True, proxy
            except Exception as e:
                pass
        return True, body, False, proxy
    else:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)


def get_page(articles, article_body, limit_date, proxy):
    text = ""
    videos = []
    photos = []
    sounds = []

    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        })
        if res.ok:
            soup = BeautifulSoup(res.text)
            title = soup.find("h1", {"class": "title pg-title"}).text.strip()
            body_texts = soup.find("div", {"class": "body-container"}).find_all("p")
            for body_text in body_texts:
                text += body_text.text
            text = text
            for cover_media in soup.find("div", {"class": "cover-media"}):
                try:
                    photos.append(cover_media.find("img").attrs['src'])
                except Exception:
                    pass
            for video in soup.find_all(text=re.compile("renderExternalContent")):
                try:
                    videos.append(str(video).replace("renderExternalContent(\"", "").replace("\")", ""))
                except Exception:
                    pass
            articles.append({"date": article_body["date"], "title": title, "text": text, "videos": videos,
                             "href": RADIO_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds
                             })
            return False, articles, proxy
        return True, articles, proxy
    except Exception:
        return get_page(articles, article_body, limit_date, update_proxy(proxy))


def parsing_radio(limit_date, proxy):
    is_not_stopped = True
    page = 0
    body = []
    last_page = None
    is_time = False
    while is_not_stopped:
        try:
            is_not_stopped, body, is_time, proxy = parsing_radio_url(page, limit_date, proxy, body)
            page += 1
        except Exception as e:
            is_not_stopped = False
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, limit_date, proxy)
        except Exception:
            pass
    if last_page is not None:
        try:
            last_page -= 1
            search_page = 0
            while not is_time and search_page < 10_000:
                is_time, articles, proxy = get_page(articles, NEW_PAGE_URL + str(last_page), limit_date, proxy)
                search_page += 1
                last_page -= 1
        except Exception:
            pass
    return articles, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_radio(datetime.strptime("21/07/2021", "%d/%m/%Y"), update_proxy(None))
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
