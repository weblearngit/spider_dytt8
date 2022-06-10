# -*- coding: utf-8 -*-
"""
@desc: 磁力链接
@version: python3
@author: shhx
@time: 2022-04-13 22:52:58
"""
from .coding_utils import str_to_base64, base64_to_str
from urllib.parse import quote, unquote, urlsplit


def url2thunder(url: str):
    """
    实际url 转为 迅雷链接
    :param url:
    :return:
    """
    url_part = urlsplit(url)
    _url = "AA{}://{}{}ZZ".format(
        url_part.scheme, url_part.netloc, quote(url_part.path)
    )
    return "thunder://" + str_to_base64(_url)


def thunder2url(url: str):
    """
    迅雷链接 转为 实际url
    :param url:
    :return:
    """
    _url = url.lstrip("thunder://")
    return unquote(base64_to_str(_url)[2:-2])
