# -*- coding: utf-8 -*-
"""
@desc: 与编码相关的
@version: python3
@author: shhx
@time: 2020/1/18 15:10
"""
import base64


def str_to_base64(code):
    """
    字符串 转 base64
    :param code:
    :return:
    """
    return base64.b64encode(code.encode("utf8")).decode("utf8")


def base64_to_str(code):
    """
    base64转 字符串
    :param code:
    :return:
    """
    return base64.b64decode(code.encode("utf8")).decode("utf8")


def get_img_base64(img_file):
    """
    :param img_file: 图片的路径及文件名
    :return: 图片的base64编码
    """
    with open(img_file, "rb") as infile:
        s = infile.read()
        return stream_to_base64(s)


def stream_to_base64(in_stream):
    """
    :param in_stream: 图片文件流
    :return: 图片的base64编码
    """
    return base64.b64encode(in_stream).decode("utf-8")
