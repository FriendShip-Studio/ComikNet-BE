from typing import List, Optional, Dict, Any
from enum import Enum
import datetime


class Origin(str, Enum):
    """
    Origin Enum
    ~~~~~~~~~~~~~~~~~~~~~
    Origin Enum is used to indicate the origin of a comic album.

    Currently, there are two origins: JMComic and Picacomic.
    """
    JMComic = "JMComic"
    Picacomic = "PicaComic"


class ComicInfo:
    """
    ComicInfo Class
    ~~~~~~~~~~~~~~~~~~~~~
    ComicInfo is a class contains the basic information of a comic album.
    """
    album_id: str
    name: str
    author: List[str]
    tags: Optional[List[str]]
    description: Optional[str]
    cover: str
    base_imgurl: Optional[str]
    total_views: Optional[int]
    total_likes: Optional[int]
    total_comments: Optional[int]
    is_liked: Optional[bool]
    is_favor: Optional[bool]
    categories: Optional[List[str]]

    def __init__(self, album_id: str, name: str, author: List[str], cover: str, description: Optional[str] = None,
                 total_views: Optional[int] = None, total_likes: Optional[int] = None,
                 total_comments: Optional[int] = None, is_liked: Optional[bool] = None,
                 is_favor: Optional[bool] = None, tags: Optional[List[str]] = None, categories: Optional[List[str]] = None):
        self.album_id = album_id
        self.name = name
        self.author = author
        self.tags = tags
        self.description = description
        self.cover = cover
        self.total_views = total_views
        self.total_likes = total_likes
        self.total_comments = total_comments
        self.is_liked = is_liked
        self.is_favor = is_favor
        self.categories = categories


class TinyComicInfo:
    """
    TinyComicInfo Class
    ~~~~~~~~~~~~~~~~~~~~~
    TinyComicInfo only contains the minimal information of a comic.

    It usually used in the search result or favorite list.
    """
    album_id: str
    name: str
    author: List[str]
    cover: str
    categories: Optional[List[str]]
    origin: Origin

    def __init__(self, album_id: str, name: str, author: List[str],
                 cover: str, origin: Origin, categories: Optional[List[str]] = None):
        self.album_id = album_id
        self.name = name
        self.author = author
        self.cover = cover
        self.categories = categories
        self.origin = origin

    def __dict__(self) -> Dict[str, Any]:
        return {
            "album_id": self.album_id,
            "name": self.name,
            "author": self.author,
            "cover": self.cover,
            "categories": self.categories,
            "origin": self.origin.value
        }

    @staticmethod
    def JM_categories_formatter(categories: List[Dict[str, str]]) -> List[str]:
        try:
            if categories[0]["title"] == categories[1]["title"]:
                return [categories[0]["title"]]
            elif categories[1]["title"] is None:
                return [categories[0]["title"]]
            else:
                return [categories[0]["title"], categories[1]["title"]]
        except KeyError:
            return ["未知分类"]


class JMComicInfo(ComicInfo):
    """
    JMComicInfo Class
    ~~~~~~~~~~~~~~~~~~~~~
    JMComicInfo is a class contains the information of a comic album in the JMComic.

    Inherited from ComicInfo class.
    """
    works: List[str]
    actors: List[str]
    series: List[Dict[str, str]]
    series_id: str
    related_list: List[Dict[str, Any]]

    def __init__(self, album_id: str, name: str, author: List[str], description: str, cover: str,
                 related_list: List[Dict[str, Any]], series: List[Dict[str, str]], series_id: str,
                 works: List[str], actors: List[str],
                 total_views: Optional[int] = None, total_likes: Optional[int] = None,
                 total_comments: Optional[int] = None, is_liked: Optional[bool] = None,
                 is_favor: Optional[bool] = None, tags: Optional[List[str]] = None):
        super().__init__(album_id, name, author, cover, description, total_views, total_likes,
                         total_comments, is_liked, is_favor, tags)
        self.series = series
        self.series_id = series_id
        self.related_list = related_list
        self.works = works
        self.actors = actors

    def __dict__(self) -> Dict[str, Any]:

        return {
            "album_id": self.album_id,
            "name": self.name,
            "author": self.author,
            "tags": self.tags,
            "description": self.description,
            "cover": self.cover,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "is_liked": self.is_liked,
            "is_favor": self.is_favor,
            "series": self.series,
            "series_id": self.series_id,
            "related_list": self.related_list,
            "works": self.works,
            "actors": self.actors
        }


class PicaComicInfo(ComicInfo):
    """
    PicaComicInfo Class
    ~~~~~~~~~~~~~~~~~~~~~
    PicaComicInfo is a class contains the information of a comic album in the PicaComic.

    Inherited from ComicInfo class.
    """
    translator: str
    isFinished: bool
    updated_at: datetime.datetime
    created_at: datetime.datetime
    allowComment: bool

    def __init__(self, album_id: str, name: str, author: List[str], description: str, cover: str,
                 categories: List[str], translator: str, isFinished: bool, updated_at: str,
                 created_at: str, allowComment: bool, total_views: Optional[int] = None,
                 total_likes: Optional[int] = None, total_comments: Optional[int] = None,
                 is_liked: Optional[bool] = None, is_favor: Optional[bool] = None,
                 tags: Optional[List[str]] = None):
        super().__init__(album_id, name, author, cover, description, total_views, total_likes,
                         total_comments, is_liked, is_favor, tags, categories)
        self.translator = translator
        self.isFinished = isFinished
        self.updated_at = datetime.datetime.strptime(
            updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.created_at = datetime.datetime.strptime(
            created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.allowComment = allowComment

    def __dict__(self) -> Dict[str, Any]:

        return {
            "album_id": self.album_id,
            "name": self.name,
            "author": self.author,
            "tags": self.tags,
            "description": self.description,
            "cover": self.cover,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "is_liked": self.is_liked,
            "is_favor": self.is_favor,
            "categories": self.categories,
            "translator": self.translator,
            "isFinished": self.isFinished,
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "allowComment": self.allowComment
        }
