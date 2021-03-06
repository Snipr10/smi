# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# radio
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString
from dateutil.parser import parse

from utils import update_proxy, parse_date

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
RADIO_PAGE_URL = "https://www.radiozenit.ru/news/page/%s"
# NEW_PAGE_URL = "news_detail.asp?id="
RADIO_URL = "https://www.radiozenit.ru/"


def parsing_radio_url(page, limit_date, proxy, body):
    try:
        res = requests.get(RADIO_PAGE_URL % page, headers={
            "user-agent": USER_AGENT
        })
    except Exception:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)
    if res.ok:
        soup = BeautifulSoup(res.text)
        tables = soup.find_all("div", {"class": "news-preview labelable"})
        if len(tables) == 0:
            return False, body, False, proxy
        for table in tables:
            article_date = parse_date(table.find("p", {"class": "news-preview__publish-time"}).text, "%d %m %Y %H:%M")
            if article_date >= limit_date:
                href = table.find("a", {"class": "news-preview__link"}).attrs.get("href")
                body.append({"date": article_date, "href": href})
            else:
                return False, body, True, proxy
        return True, body, False, proxy
    else:
        return parsing_radio_url(page, limit_date, update_proxy(proxy), body)


def get_page(articles, article_body, proxy):
    title = ""
    text = ""
    photos = []
    sounds = []
    videos = []
    try:
        res = requests.get(RADIO_URL + article_body['href'], headers={
            "user-agent": USER_AGENT
        })
        if res.ok:
            soup = BeautifulSoup(res.text)
            article = soup.find("article", {"class": "article article__news"})
            title = article.find("h1", {"class": "title title_s_reduced article__title"}).text
            for p in article.find("div", {"class": "article__inner"}).find_all("p"):
                text += p.text
                try:
                    text += f" ({p.contents[0].attrs['href']}) "
                except Exception:
                    pass
                text += "\n"
            try:
                for img in article.find("div", {"class": "article__inner"}).find_all("img"):
                    try:
                        photos.append(img.attrs["src"])
                    except Exception:
                        pass
            except Exception:
                pass
            articles.append({"date": article_body['date'], "title": title, "text": text.replace("??", " ").strip(),
                             "href": RADIO_URL + article_body['href'],
                             "photos": photos,
                             "sounds": sounds,
                             "videos": videos
                             })

            return False, articles, proxy
        return False, articles, proxy
    except Exception:
        return get_page(articles, article_body, update_proxy(proxy))


def parsing_radio(limit_date, proxy):
    is_not_stopped = True
    page = 1
    body = []
    while is_not_stopped:
        try:
            is_not_stopped, body, is_time, proxy = parsing_radio_url(page, limit_date, proxy, body)
            page += 1
        except Exception:
            is_not_stopped = False
    articles = []
    for article in body:
        try:
            is_time, articles, proxy = get_page(articles, article, proxy)
        except Exception:
            pass

    return articles, proxy


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_radio(datetime.strptime("21/05/2021", "%d/%m/%Y"), update_proxy(None))
    print(1)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
