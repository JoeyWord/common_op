"""
create by jwhv587 at 2021/9/20
"""

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from urllib.request import urlretrieve

url="https://www.xmanhua.com/10xm/"
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163"}
# params = {"start":start_idx,"filter":""}
req = requests.get(url,headers=headers,timeout=10)


domain_url = "https://www.xmanhua.com"
if not req.encoding:
    req.encoding = 'utf-8'
html = req.text
soup = BeautifulSoup(html, 'lxml')
cl = soup.select("div#chapterlistload")
lis = cl[0].select("a")
print(f'cl len: {len(cl)} and lis: {len(lis)}')
folds = []
for idx, li in tqdm(enumerate(lis), desc='chapter:'):
    f_nm = "_".join(li.text.split())
    path = li.attrs["href"]
    folds.append(f_nm)

    inner_url = urljoin(domain_url, path)
    print(f"{f_nm} href:{path} and inner url is:{}")
    #     get_pic(f_nm,inner_url)
    if idx > 1:
        break

def get_pic(url,tag,restore):
    """

    :param url:
    :param tag:
    :param restore:
    :return:
    """
    req=requests.get(url,headers=headers,timeout=5)
    if req.status_code==200:
        req.encoding='utf-8'
        html = req.text
        soup = BeautifulSoup(html, 'lxml')
        pic_links=soup.select(tag)
        print(f"pic link nums:{len(pic_links)}")
        for pic in pic_links:
            urlretrieve(pic,restore)
    else:
        print(f"not normal req with code:{req.status_code}")
        raise RuntimeError()