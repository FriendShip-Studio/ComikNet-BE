import requests
from requests.cookies import RequestsCookieJar
from src.config.mirror import mirror
from bs4 import BeautifulSoup
from src.models.comic import ComicInfo


def get_comic_info(id: str, cookies: RequestsCookieJar) -> dict:

    if(id.startswith("JM")):
        id = id[2:]

    req = requests.get(f"https://{mirror}/album/{id}/", cookies=cookies)

    document = BeautifulSoup(req.content, "lxml")

    title = document.find(
        "div", class_="panel-heading").find("h1").text.strip()
    cover = document.find("div", class_="col-lg-5").find("img").attrs["src"]
    serial = document.find(
        "div", class_="absolute train-number").text.strip().split("\n")[0][4:]
    intro = document.find(
        "div", id="intro-block").find("div", class_="p-t-5 p-b-5").text.strip()[3:]

    comic_info = {
        "title": title,
        "cover": cover,
        "serial": serial,
        "intro": intro,
        "series": None,
        "characters": None,
        "tags": None,
        "author": None
    }

    blockdata = document.find(
        "div", class_="col-lg-7").find_all("div", class_="tag-block")

    for data in blockdata:
        data_str: str = data.text.strip()

        if(data_str.startswith("作品： ")):
            if(data_str[5:]):
                comic_info["series"] = [dat.strip()
                                        for dat in data_str[5:].split("\n")]

        if(data_str.startswith("登场人物：")):
            if(data_str[6:]):
                comic_info["characters"] = [dat.strip()
                                            for dat in data_str[6:].split("\n")]

        if(data_str.startswith("标签： ")):
            if(data_str[5:]):
                comic_info["tags"] = [dat.strip()
                                      for dat in data_str[5:].split("\n")]

        if(data_str.startswith("作者： ")):
            if(data_str[5:]):
                comic_info["author"] = [dat.strip()
                                        for dat in data_str[5:].split("\n")]

    return comic_info
