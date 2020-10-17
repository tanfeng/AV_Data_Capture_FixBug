import sys
sys.path.append('../')
import re
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *
from WebCrawler import fanza

def getActorPhoto(htmlcode): #//*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    d={}
    for i in a:
        l=i.a['href']
        t=i.get_text()
        html = etree.fromstring(get_html(l), etree.HTMLParser())
        p=str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']")
        p2={t:p}
        d.update(p2)
    return d
def getTitle(htmlcode):  #获取标题
    doc = pq(htmlcode)
    title=str(doc('div.container h3').text())
    return title
def getStudio(htmlcode): #获取厂商 已修改
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = ''
    try:
        for i in range (4, 10):
            if '製作商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/span/text()')).strip(" ['']"):
                result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/a/text()')).strip(" ['']")
                break
    except:
        pass
    return result
def getYear(htmlcode):   #获取年份
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getCover(htmlcode):  #获取封面链接
    doc = pq(htmlcode)
    image = doc('a.bigImage')
    return image.attr('href')
def getRelease(htmlcode): #获取出版日期
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getRuntime(htmlcode): #获取分钟 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[3]/text()')).strip(" ['']分鐘")
    return result
def getActor(htmlcode):   #获取女优
    b=[]
    soup=BeautifulSoup(htmlcode,'lxml')
    a=soup.find_all(attrs={'class':'star-name'})
    for i in a:
        b.append(i.get_text().strip())
    return b
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getDirector(htmlcode): #获取导演 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = ''
    try:
        for i in range (4, 10):
            if '導演:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/span/text()')).strip(" ['']"):
                result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/a/text()')).strip(" ['']")
                break
    except:
        pass
    return result
def getCID(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    #print(htmlcode)
    string = html.xpath("//a[contains(@class,'sample-box')][1]/@href")[0]
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
def getSerise(htmlcode):   #获取系列 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = ''
    try:
        for i in range (4, 10):
            if '發行商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/span/text()')).strip(" ['']"):
                result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p['+str(i)+']/a/text()')).strip(" ['']")
                break
    except:
        pass
    return result
def getTag(htmlcode):  # 获取标签
    tag = []
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find_all(attrs={'class': 'genre'})
    for i in a:
        if 'onmouseout' in str(i):
            continue
        tag.append(translateTag_to_sc(i.get_text()))
    return tag

def main(number):
    try:
        htmlcode = get_html('https://www.javbus.com/' + number)
        try:
            dww_htmlcode = fanza.main_htmlcode(getCID(htmlcode))
        except:
            dww_htmlcode = ''
        dic = {
            'title': getTitle(htmlcode).replace(getNum(htmlcode),'').strip(),
            'studio': getStudio(htmlcode),
            'year': str(re.search('\d{4}', getYear(htmlcode)).group()),
            'outline': getOutline(dww_htmlcode),
            'runtime': getRuntime(htmlcode),
            'director': getDirector(htmlcode).strip(),
            'actor': getActor(htmlcode),
            'release': getRelease(htmlcode),
            'number': getNum(htmlcode),
            'cover': getCover(htmlcode),
            'imagecut': 1,
            'tag': getTag(htmlcode),
            'label': getSerise(htmlcode),
            'actor_photo': getActorPhoto(htmlcode),
            'website': 'https://www.javbus.com/' + number,
            'source': 'javbus.py',
            'series': getSerise(htmlcode),
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,
                        separators=(',', ':'), )  # .encode('UTF-8')
        return js
    except:
        data = {
            "title": "",
        }
        js = json.dumps(
            data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
        )
        return js

if __name__ == "__main__" :
    print(main('ipx-292'))
