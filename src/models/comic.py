class ComicInfo():

    def __dict__(self, title: str, cover: str, serial: str,
                 intro: str = "", author: list[str] = None,
                 characters: list[str] = None, tags: list[str] = None,
                 series: list[str] = None) -> None:

        self.comic_info = {
            "title": title,
            "cover": cover,
            "serial": serial
        }

        if(intro != ""):
            self.comic_info["intro"] = intro
        if(author != None):
            self.comic_info["author"] = author
        if(characters != None):
            self.comic_info["characters"] = characters
        if(tags != None):
            self.comic_info["tags"] = tags
        if(series != None):
            self.comic_info["series"] = series

        return self.comic_info
