import sys
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
from WebCrawler import fanza
from http.cookies import SimpleCookie
import time
import json
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath("/html/body/section/div/h2/strong/text()")[0]
    return result
def getActor(a):  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"演員")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"演員")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace(",\\xa0", "").replace("'", "").replace(' ', '').replace(',,', '').lstrip(',').replace(',', ', ').replace('N/A', '')
def getActorPhoto(actor): #//*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d={}
    for i in a:
        p={i:''}
        d.update(p)
    return d
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時間")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時間")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+')
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/a/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total
    except:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total

def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getSeries(a):
    #/html/body/section/div/div[3]/div[2]/nav/div[7]/span/a
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getCID(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        string = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except: # 2020.7.17 Repair Cover Url crawl
        string = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
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
def main(number):
    try:
        number = number.upper()

        # raw_cookies, user_agent = get_javdb_cookie()
        #
        # if not raw_cookies:
        #    return json.dumps({}, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        #
        # s_cookie = SimpleCookie()
        # s_cookie.load(raw_cookies)
        # cookies = {}
        # for key, morsel in s_cookie.items():
        #    cookies[key] = morsel.value
        #
        # correct_url = ''

        time.sleep(3)

        try:
            # 先尝试使用ajax
            query_result = get_html('https://javdb.com/videos/search_autocomplete.json?q='+number)

            items = json.loads(query_result)

            links = []
            titles = []

            for item in items:
                if item['number'].upper() == number:
                    links.append('/v/'+item['uid'])
                    titles.append(item['title'])

            if len(links) > 1:
                for i, link in enumerate(links):
                    print(str(i+1)+": "+titles[i])
                    print('https://javdb.com'+link)

                index = int(input("input index: "))-1

                if index < 0 or index >= len(links):
                    raise ValueError("out of range")

                correct_url = links[index]
            else:
                correct_url = links[0]
        except:
            ok=0

            for i in range(1,10):
                try:
                    query_result = get_html('https://javdb.com/search?q=' + number + '&f=all')
                except:
                    query_result = get_html('https://javdb4.com/search?q=' + number + '&f=all')

                html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()

                if str(html.xpath('/html/body/section/div/div[4]/article/div/text()')).strip(" ['']") == '':
                    ok=1
                    break

                print("请求过于频繁，重试："+str(i))
                time.sleep(30)

            if ok==0:
                raise ValueError("retry max")

            # javdb sometime returns multiple results,
            # and the first elememt maybe not the one we are looking for
            # iterate all candidates and find the match one
            urls = html.xpath('//*[@id="videos"]/div/div/a/@href')
            ids =html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "uid")]/text()')
            allTitles=html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "video-title")]/text()')

            links = []
            titles = []

            for i, id in enumerate(ids):
                if id.upper() == number:
                    links.append(urls[i])
                    titles.append(allTitles[i])

            if len(links) > 1:
                for i, link in enumerate(links):
                    print(str(i+1)+": "+titles[i])
                    print('https://javdb.com'+link)

                index = int(input("input index: "))-1

                if index < 0 or index >= len(links):
                    raise ValueError("out of range")

                correct_url = links[index]
            else:
                correct_url = links[0]

        detail_page = get_html('https://javdb.com' + correct_url)

        # # If gray image exists ,then replace with normal cover
        # cover_small = getCover_small(query_result, index=ids.index(number))
        # if 'placeholder' in cover_small:
        #     cover_small = getCover(detail_page)

        try:
            dww_htmlcode = fanza.main_htmlcode(getCID(detail_page))
        except:
            dww_htmlcode = ''

        dic = {
            'actor': getActor(detail_page),
            'title': getTitle(detail_page).replace(getNum(detail_page),'').strip(),
            'studio': getStudio(detail_page),
            'outline': getOutline(dww_htmlcode),
            'runtime': getRuntime(detail_page),
            'director': getDirector(detail_page),
            'release': getRelease(detail_page),
            'number': getNum(detail_page),
            'cover': getCover(detail_page),
            # 'cover_small': cover_small,
            'imagecut': 1,
            'tag': getTag(detail_page),
            'label': getLabel(detail_page),
            'year': getYear(getRelease(detail_page)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': getActorPhoto(getActor(detail_page)),
            'website': 'https://javdb.com' + correct_url,
            'source': 'javdb.py',
            'series': getSeries(detail_page),
        }

        title = dic['title']

        if title.find('無碼') >= 0:
            raise ValueError("unsupport")

    except Exception as e:
        # print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    print(main('ipx-292'))
