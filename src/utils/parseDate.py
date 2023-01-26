month_translate = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}


def parseDate(cinfo: list):
    res = []
    for comment in cinfo:
        comment["addtime"] = f"{comment['addtime'][-4:]}-{month_translate[comment['addtime'][:3]]}-{comment['addtime'][4:6]}"
        res.append(comment)
    return res
