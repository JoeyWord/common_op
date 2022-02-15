#!/usr/bin/env/py35
# coding=utf-8
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
def cityScrapy(url,write2file):
    try:
        html = urlopen(url)
    except Exception as e:
        print(e)
    else:
        try:
            city_file = open(write2file, mode='w', encoding='utf-8')
        except:
            print("open file failed")
        soup = BeautifulSoup(html.read(),'lxml')
        table_need = soup.find("table",{"border":1})
        trs = table_need.find_all('tr')
        head = []
        citys = []
        contents = []
        count = 0
        for tr in trs:
            count += 1
            if count == 1:
                tds = tr.find_all('td')
                for td in tds:
                    text = td.get_text()
                    text = re.sub('\s+', '', text)
                    head.append(text)
            else:
                tds = tr.find_all('td')
                tmp = []
                count_td = 0
                for td in tds:
                    count_td += 1
                    text = td.get_text()
                    text = re.sub('\s+', '', text)
                    if count_td ==2:
                        citys.append(text)
                        city_file.write(text + ' ' + str(10) + ' ' + 'ns' + '\n')
                        if text.endswith('市'):
                            abbr_city = text.replace('市','')
                            citys.append(abbr_city)
                            city_file.write(abbr_city + ' ' +str(10) + ' ' + 'ns' + '\n')
                    tmp.append(text)
                contents.append(tmp)

if __name__ == '__main__':
    cityScrapy('http://www.hotelaah.com/dijishi.html','data/citys.txt')
