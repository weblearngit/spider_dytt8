# -*- coding: utf-8 -*-
"""
@desc:
@version: python3
@author: shhx
@time: 2019/11/22 11:39

参考：https://github.com/guapier/dytt8
调用：
scrapy crawl dytt8 -o movies.csv

2022-04-12 使用 -o 保存输出结果
    用时 4.5h 抓取 12469，10512 有值
    使用csv格式，有部分数据中含 逗号，导致数据行错误

2022-04-13 使用pipeline存储exce方式
    用时 12分钟 抓取 15030 条
    没有抓取到 https://www.ygdy8.com/html/gndy/jddy/20140711/45659.html，记录url，对比结果

2022-04-14 修改下载url的获取方式
    用时 17分钟 抓取 15042 个网页，其中14180条记录
"""
import re
import scrapy
from pyquery import PyQuery as pq
from .url_thunder import url2thunder, thunder2url


class Dytt8Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()  # 片名
    title = scrapy.Field()  # 标题名
    category = scrapy.Field()  # 类别
    publish_year = scrapy.Field()  # 年代
    country = scrapy.Field()  # 产地
    language = scrapy.Field()  # 语言
    captions = scrapy.Field()  # 字幕
    introduce = scrapy.Field()  # 简介
    detail_url = scrapy.Field()  # 详情页
    download_url = scrapy.Field()  # 下载地址
    thunder_url = scrapy.Field()  # 迅雷下载地址


def get_settings(filename):
    settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "app.middlewares.log_request.LogURLMiddleware": 100
        },
        "ITEM_PIPELINES": {"app.pipelines.file_save.ExcelPipeline": 100},
        "EXCEL_SAVE": {
            "title": [
                {"name": "标题名", "value": "title"},
                {"name": "译名", "value": "name"},
                {"name": "类别", "value": "category"},
                {"name": "年代", "value": "publish_year"},
                {"name": "产地", "value": "country"},
                {"name": "语言", "value": "language"},
                {"name": "字幕", "value": "captions"},
                {"name": "简介", "value": "introduce"},
                {"name": "详情页", "value": "detail_url"},
                {"name": "下载地址", "value": "download_url"},
                {"name": "迅雷下载地址", "value": "thunder_url"},
            ],
            "output_path": f"./output-{filename}.xlsx",
        },
        "LOG_URL_PATH": f"./output-urls-{filename}.txt",
    }
    return settings


class Detail:
    def detail(self, response):
        doc = pq(response.text)
        download_url, thunder_url = self.detail_download_url(doc)
        if not download_url:
            return
        zoom_text = doc("div[id=Zoom]").text()
        name = re.compile("译\s*名(.*)").findall(zoom_text)
        category = re.compile("类\s*别(.*)").findall(zoom_text)
        publish_year = re.compile("年\s*代(.*)").findall(zoom_text)
        country = re.compile("产\s*地(.*)").findall(zoom_text)
        language = re.compile("语\s*言(.*)").findall(zoom_text)
        captions = re.compile("字\s*幕(.*)").findall(zoom_text)
        introduce = self.detail_introduce(doc("div[id=Zoom]"))
        item_dict = {
            "title": doc("div[class=title_all] >h1").text(),
            "name": name[0].strip() if name else "",
            "category": category[0].strip() if category else "",
            "publish_year": publish_year[0].strip() if publish_year else "",
            "country": country[0].strip() if country else "",
            "language": language[0].strip() if language else "",
            "captions": captions[0].strip() if captions else "",
            "introduce": introduce,
            "detail_url": response.url,
            "download_url": download_url,
            "thunder_url": thunder_url,
        }
        yield Dytt8Item(**item_dict)

    def detail_download_url(self, doc):
        """获取下载链接"""
        download_url = []
        for each in doc.find("a").items():
            a_href = each.attr("href")
            if not a_href:
                continue
            if a_href.startswith("thunder://"):
                download_url.append(thunder2url(a_href))
            elif a_href.startswith("ftp://"):
                download_url.append(a_href)
            elif a_href.startswith("magnet:"):
                download_url.append(a_href)
        thunder_url = [
            url2thunder(url) if url.startswith("ftp://") else url
            for url in download_url
        ]
        return download_url, thunder_url

    def detail_introduce(self, doc):
        """获取简介"""
        introduce = ""
        for row in doc.find("p").items():
            introduce = self._introduce_text(row.text())
            if introduce:
                break
        if not introduce:
            introduce = self._introduce_text(doc.text())
        return introduce

    def _introduce_text(self, text):
        """获取简介"""
        introduce = re.compile("简\s*介([\s\S]*)").findall(text)
        if introduce:
            return introduce[0].lstrip(":").strip()
        return ""


class A(scrapy.Spider, Detail):
    """
    获取 电影、电视剧
    """

    name = "dytt8"
    allowed_domains = [
        "www.dytt8.net",
        "m.dytt8.net",
        "www.ygdy8.com",
        "www.dydytt.net",
    ]
    headers = {
        "connection": "keep-alive",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/71.0.3578.98 Safari/537.36",
        "dnt": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cookie": "XLA_CI=97928deaf2eec58555c78b1518df772a",
    }

    custom_settings = get_settings(name)

    def start_requests(self):
        base_url = "https://www.dytt8.net/html/{}/index.html"
        categories = [
            "gndy/china",
            "gndy/rihan",
            "gndy/oumei",
            "gndy/dyzz",
            "tv/hytv",
            "tv/rihantv",
            "tv/oumeitv",
        ]
        for category in categories:
            yield scrapy.Request(
                base_url.format(category),
                headers=self.headers,
                callback=self.parse,
            )

    def parse(self, response):
        # xpath('//div[contains(@class,"a") and contains(@class,"b")]') #它会取class含有有a和b的元素
        detail_urls = response.xpath('//a[@class="ulink"]/@href').extract()
        detail_urls = [url for url in detail_urls if "index" not in url]

        for url in detail_urls:
            yield response.follow(
                url, headers=self.headers, callback=self.detail,
            )
        next_page = response.xpath(
            './/a[contains(text(),"下一页")]/@href'
        ).extract_first()
        if next_page is not None:
            yield response.follow(
                next_page, headers=self.headers, callback=self.parse
            )


class B(A):
    """
    高分经典
    """

    name = "dytt8_gf"

    custom_settings = get_settings(name)

    def start_requests(self):
        base_url = "https://m.dytt8.net/html/gndy/jddy/20160320/50523.html"
        yield scrapy.Request(
            base_url, headers=self.headers, callback=self.parse,
        )

    def parse(self, response):
        doc = pq(response.body)
        for each in doc("div[id=Zoom]").find("p").items():
            p_a = list(each.find("a").items())
            if not p_a:
                continue
            a_href = p_a[0].attr("href")
            yield response.follow(
                a_href, headers=self.headers, callback=self.detail,
            )

        next_page = response.xpath(
            './/a[contains(text(),"下一页")]/@href'
        ).extract_first()
        if next_page is not None:
            yield response.follow(
                next_page, headers=self.headers, callback=self.parse
            )


class C(scrapy.Spider, Detail):
    """
    调试抓取
    """

    name = "dytt8_debug"
    start_urls = ["https://www.ygdy8.com/html/gndy/dyzz/20210826/61782.html"]

    def parse(self, response):
        return self.detail(response)
