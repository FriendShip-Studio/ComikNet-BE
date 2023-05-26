from enum import Enum


class PicaSortRule(str, Enum):

    Time = "dd"
    TimeReversed = "da"
    Favorite = "ld"
    RatingPoint = "vd"


class JMSortRule(str, Enum):

    Time = "mr"
    Click = "mv"
    Images = "mp"
    Favorite = "tf"
