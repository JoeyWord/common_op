#!/usr/bin/env/py35
# coding=utf-8

import requests
import os
import time
import threading

from bs4 import BeautifulSoup
from urllib.request import urlretrieve

from entity_commonFun_jin import multiThread,get_logger

log_file = os.path.join("log","movie.log")
logger = get_logger(log_file)

url = "https://movie.douban.com/top250"
# url="https://www.dm5.com/manhua-shengdoushixingshimingwangshenhua/"
if not os.path.exists('pic'):
    os.mkdir('pic')


def parse_url(url,start_idx):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163"}
    params = {"start":start_idx,"filter":""}
    try:
        req = requests.get(url,headers=headers,params=params,timeout=10)
    except Exception as e:
        print(e)
    if not req.encoding:
        req.encoding = 'utf-8'
    html = req.text
    soup = BeautifulSoup(html,'lxml')
    divs = soup.select("div[class=item]")
    movie_name = []
    movie_pic = []
    for id,div_tag in enumerate(divs):
        name = div_tag.select("span[class=title]")
        movie_name.append(name[0].text)
        pic = div_tag.select("div[class=pic] > a > img")
        if not hasattr(pic[0],"attrs"):
            continue
        pic_src = pic[0].attrs["src"]
        file_name = os.path.join('pic',str(1+id+start_idx)+'.jpg')
        urlretrieve(pic_src,file_name)
    logger.info(", ".join(movie_name))
    return movie_name


if __name__ == '__main__':
    time0 = time.time()
    start_idxs = range(0,250,25)
    movie_all = []
    """
    for i,idx in enumerate(start_idxs):
        movie_info = parse_url(idx)
        print("movie length={} and top3 res={} for page {}".format(len(movie_info),movie_info[:3],i))
        movie_all.extend(movie_info)
    """
    time1 = time.time()
    #print("all movie get cost time={}s".format(time1-time0))
    #multithread compute
    threads = []
    for idx in start_idxs:
        thread = threading.Thread(target=parse_url,args=(url,idx,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    #multiThread(20,"movie_thread",list(start_idxs),parse_url,**kwargs)
    time2 = time.time()
    print("multiThread cost time={}s".format(time2-time1))



