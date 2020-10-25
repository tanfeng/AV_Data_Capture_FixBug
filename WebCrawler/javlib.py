import sys
sys.path.append('../')
import json
import bs4
import re
from bs4 import BeautifulSoup
from lxml import html
from http.cookies import SimpleCookie
from WebCrawler import fanza
from lxml import etree
from ADC_function import get_javlib_cookie, get_html, translateTag_to_sc

def getCID(lx):
    string = get_from_xpath(lx, '//*[@id="video_jacket_img"]/@src')
    result = re.search('/([^/]+)/[^/]+\.jpg', string, flags=0).group(1)
    return result

def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        detail = html.xpath("//div[contains(@class,'mg-b20 lh4')]/text()")[0].replace('\n','').strip()
        if detail == "":
            raise ValueError("no detail")
    except:
        try:
            detail = html.xpath("//div[contains(@class,'mg-b20 lh4')]/p/text()")[0].replace('\n','').strip()
            if detail == "":
                raise ValueError("no detail")
        except:
            try:
                detail = html.xpath("string(//div[contains(@class,'mg-b20 lh4')])").replace('\n','').strip()
            except:
                detail = ''
    return detail

def get_link_count(lx):
    t = lx.xpath('/html/body/div[3]/div[2]/div[2]/div/div')
    return len(t)

def get_link(lx, i):
    id = get_from_xpath(lx, '/html/body/div[3]/div[2]/div[2]/div/div['+str(i)+']/a/div[1]/text()')
    href = get_from_xpath(lx, '/html/body/div[3]/div[2]/div[2]/div/div['+str(i)+']/a/@href').strip('.')
    title = get_from_xpath(lx, '/html/body/div[3]/div[2]/div[2]/div/div['+str(i)+']/a/div[2]/text()')

    return id, href, title

def getTag(tagsStr):
    if tagsStr == '':
        return
    tags = tagsStr.replace("'", '').replace(" ", '').split(',')
    total = []
    for i in tags:
        try:
            total.append(translateTag_to_sc(i))
        except:
            pass
    return total

def main(number: str):
    number = number.upper()
    oldNumber = number

    if re.match(r'^([0-9]+)ID-(.+)$', number):
        g = re.search(r'^([0-9]+)ID-(.+)$', number)
        number = 'ID-'+g[1]+g[2]

    # raw_cookies, user_agent = get_javlib_cookie()
    #
    # #Blank cookies mean javlib site return error
    # if not raw_cookies:
    #    return json.dumps({}, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
    #
    # #Manually construct a dictionary
    # s_cookie = SimpleCookie()
    # s_cookie.load(raw_cookies)
    # cookies = {}
    # for key, morsel in s_cookie.items():
    #    cookies[key] = morsel.value

    # Scraping
    result = get_html(
        "http://www.b47w.com/cn/vl_searchbyid.php?keyword={}".format(number),
        # cookies=cookies,
        # ua=user_agent,
        return_type="object"
    )
    soup = BeautifulSoup(result.text, "html.parser")
    lx = html.fromstring(str(soup))

    multiLabel = get_from_xpath(lx, '//*[@id="rightcolumn"]/div[1]/text()')
    if multiLabel.find('识别码搜寻结果') > 0:
        links = []
        titles = []

        for i in range(1, get_link_count(lx)+1):
            id, href, title = get_link(lx, i)
            if title.count('（ブルーレイディスク）') > 0:
                continue
            if id.upper() == number:
                links.append('http://www.b47w.com/cn'+href)
                titles.append(title)

        link = ''

        if len(links) > 1:
            for i, link in enumerate(links):
                print(str(i+1)+": "+titles[i])
                print(link)

            index = int(input("input index: "))-1

            if index < 0 or index >= len(links):
                raise ValueError("out of range")

            link = links[index]
        else:
            link = links[0]

        if link == '':
            raise ValueError("no match")

        result = get_html(
            link,
            return_type="object"
        )
        soup = BeautifulSoup(result.text, "html.parser")
        lx = html.fromstring(str(soup))

    try:
        dww_htmlcode = fanza.main_htmlcode(getCID(lx))
    except:
        dww_htmlcode = ''

    realnumber = get_table_el_td(soup, "video_id")
    if oldNumber != number:
        realnumber = oldNumber

    if "/?v=jav" in result.url:
        dic = {
            "title": get_title(lx, soup),
            "studio": get_table_el_single_anchor(soup, "video_maker"),
            "year": get_table_el_td(soup, "video_date")[:4],
            "outline": getOutline(dww_htmlcode),
            "director": get_table_el_single_anchor(soup, "video_director"),
            "cover": get_cover(lx),
            "imagecut": 1,
            "actor_photo": "",
            "website": result.url.replace('www.b47w.com', 'www.javlibrary.com'),
            "source": "javlib.py",
            "actor": get_table_el_multi_anchor(soup, "video_cast"),
            "label": get_table_el_single_anchor(soup, "video_label"),
            "tag": getTag(get_table_el_multi_anchor(soup, "video_genres")),
            "number": realnumber,
            "release": get_table_el_td(soup, "video_date"),
            "runtime": get_from_xpath(lx, '//*[@id="video_length"]/table/tr/td[2]/span/text()'),
            "series":'',
        }
    else:
        dic = {}


    return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


def get_from_xpath(lx: html.HtmlElement, xpath: str) -> str:
    return lx.xpath(xpath)[0].strip()


def get_table_el_single_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tag = soup.find(id=tag_id).find("a")

    if tag is not None:
        return tag.string.strip()
    else:
        return ""


def get_table_el_multi_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("a")

    return process(tags)


def get_table_el_td(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("td", class_="text")

    return process(tags)


def process(tags: bs4.element.ResultSet) -> str:
    values = []
    for tag in tags:
        value = tag.string
        if value is not None and value != "----":
            values.append(value)

    return ",".join(x for x in values if x)


def get_title(lx: html.HtmlElement, soup: BeautifulSoup) -> str:
    title = get_from_xpath(lx, '//*[@id="video_title"]/h3/a/text()')
    number = get_table_el_td(soup, "video_id")

    return title.replace(number, "").strip()


def get_cover(lx: html.HtmlComment) -> str:
    return "http:{}".format(get_from_xpath(lx, '//*[@id="video_jacket_img"]/@src'))


if __name__ == "__main__":
    lists = ["DVMC-003", "GS-0167", "JKREZ-001", "KMHRS-010", "KNSD-023"]
    #lists = ["DVMC-003"]
    for num in lists:
        print(main(num))
