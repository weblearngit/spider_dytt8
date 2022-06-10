# -*- coding: utf-8 -*-
"""
@desc: 记录url的访问日志
@version: python3
@author: shhx
@time: 2022/4/13 13:52
"""
import time


class LogURLMiddleware:
    def __init__(self, spider_name):
        self.log_path_obj = open(f"output-{spider_name}-{time.time()}.log", "wb")

    @classmethod
    def from_crawler(cls, crawler):
        """
        获取spider的settings参数,返回中间件实例对象
        """
        return cls(crawler.spider.name)

    def process_request(self, request, spider):
        """
        return
            None: 继续处理Request
            Response: 返回Response
            Request: 重新调度
        raise IgnoreRequest:  process_exception -> Request.errback
        """
        self.log_path_obj.write(f"{request.url}\n".encode("utf8"))
