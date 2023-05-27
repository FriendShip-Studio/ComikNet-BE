from enum import Enum
from typing import Any, Union, List, Optional
from pydantic import BaseModel

from models.sort import PicaSortRule, JMSortRule


class StandardResponse(BaseModel):
    """
    StandardResponse Class
    ~~~~~~~~~~~~~~~~~~~~~
    StandardResponse is a model for the standard response of the API.

    When the ComikNet-BE connects to the upstream successfully, it will return a StandardResponse.
    If the upstream returns an error, the `data` field will be None and the `error_msg` field will be
    filled with the error message or the error code.

    """

    status_code: int
    data: Optional[Any] = None
    error_msg: Optional[str] = None


class SearchMode(str, Enum):
    """
    SearchMode is an enum class for the search mode.

    Enum: `JM`, `Pica`, `Mix`
    """

    JM = "JM"
    Pica = "Pica"
    Mix = "Mix"


class SearchInfo(BaseModel):
    """
    SearchInfo Class
    ~~~~~~~~~~~~~~~~~~~~~
    SearchInfo is a model for a search request.
    """

    mode: SearchMode
    query: str
    page: int = 1
    sort: Optional[Union[JMSortRule, PicaSortRule]] = None
    append_query: Optional[List[str]] = None
