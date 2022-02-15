#!/usr/bin/env/py35
# coding=utf-8
# !/usr/bin/python3
# -*- coding:utf-8 -*-
import jieba.posseg as pseg
# import pymysql
import re
# import pymssql
import threading
import time
import numpy as np
import pickle
import os
import logging
from multiprocessing import Pool

# def odbc_connect(**kwargs):
#     """
#     kwargs info:host,port,database,user,passwd
#     """
#     #odbcHandler = 'DRIVER={SQL Server};SERVER=%s,%s;DATABASE=%s;UID=%s;PWD=%s'%(kwargs["host"],kwargs["port"],kwargs['db'],kwargs["user"],kwargs["passwd"])
#     try:
#         conn = pymssql.connect(host=kwargs["host"],port=kwargs["port"],user=kwargs["user"],password=kwargs["passwd"],database=kwargs['db'],charset=kwargs["charset"])
#     except Exception as e:
#         print(e)
#     else:
#         return conn


def mysqlConnect(host,port,user,password,db,charset='utf8'):
    connectDict=dict(host=host,port=port,user=user,password=password,db=db,charset=charset)
    try:
        conn=pymysql.connect(**connectDict)
    except Exception as e:
        print(e)
        return None
    return conn


def clean(company_name):
    name = re.sub('\（.*\）', '', company_name)
    name = re.sub('\s+', '', name)
    name = re.sub('\W+', '', name)
#   name = re.sub('[a-zA-Z0-9_]+', '', name)
    return name

def tokenize(company_name,uni=True):
    company_name = clean(company_name)
    seg = pseg.cut(company_name)
    if uni:
        word_set = set()
        for word,pos in seg:
            word_set.add(word)
        return list(word_set)
    else:
        word_ls =[]
        for word,pos in seg:
            word_ls.append(word)
        return word_ls

def idfValue(lines):
    count = 0
    freq_dict = {}
    idf_dict = {}
    for line in lines:
        count += 1
        if type(line) is not str:
            words = tokenize(line[0])
        else:
            words = tokenize(line)
        for word in words:
            if word not in freq_dict:
                freq_dict[word] = 0
            freq_dict[word] += 1
    for word in freq_dict:
        idf_dict[word] = round(count/freq_dict[word],2)
    return idf_dict

def maxLen(inputs):
    max_len = 0
    for input in inputs:

        if type(input) == str:
            len_in = len(input)
        else:
            assert type(input[0]) == str
            len_in = len(input[0])
        if len_in >= max_len:
            max_len = len_in
    return max_len
def corpNameExtract(company_name, sub_len):
    common_words = ['公司','股份','责任','有限']
    company_name = clean(company_name)
    seg = pseg.cut(company_name)
    id = 0;
    ns_id = 0;
    nz_id = 0
    nr_id = 0
    cache_id_ns = 0
    cache_id_nr = 0
    cache_id_nz = 0
    cache_id_v = 0
    name_extract = ''
    for word, pos in seg:
        id += 1
        if pos == 'ns':
            ns_id += 1
            if ns_id == id:
                name_extract += word
                cache_id_ns = id
            else:
                break

        if pos == 'nr':
            nr_id += 1
            if nr_id == id:
                name_extract += word
                cache_id_nr = id
            else:
                break

        if pos in ['nz','nt']:
            nz_id += 1
            cache_id_nz = id
            name_extract += word
        elif pos == 'n':
            sub_ls = set()
            for i in range(0, sub_len + 1, 2):
                sub_str = company_name[i:(i+2)]
                sub_ls.add(sub_str)
            if word in sub_ls:
                name_extract += word

        if pos == 'vn':
            cache_id_next = id
            if cache_id_next == (cache_id_nz+1) or np.abs(cache_id_next-max(cache_id_nr,cache_id_ns)) == 1:
                common_count = 0
                for common_word in common_words:
                    if common_word not in word:
                        common_count += 1
                if common_count == len(common_words):
                    name_extract += word

        if pos == 'v':
            cache_id_v = id
            if cache_id_v == 1:
                name_extract += word
            elif cache_id_v == (ns_id+1):
                name_extract += word
        if pos == 'j':
            cache_id_j = id
            if cache_id_j == (cache_id_v+1):
                name_extract += word
    check_ex = pseg.cut(name_extract)
    count = 0
    check_word = ""
    for word,pos in check_ex:
        count += 1
        if pos in ['ns','nr']:
            check_word += word
    if count ==1 and len(check_word) > 0:
        name_extract = ""
    return name_extract

def extractNameDrop(company_name,seperate_word,idf_thr,idf_dict):
    common_words = ['公司','股份','责任','有限','分公司','子公司','科技','技术']
    company_name = clean(company_name)
    seg = pseg.cut(company_name)
    for word,pos in seg:
        if pos == 'ns':
            company_name = company_name.replace(word,"")
        if word in idf_dict:
            if seperate_word in idf_dict:
                if idf_dict[word] < idf_dict[seperate_word]:
                    company_name = company_name.replace(word,"")
            else:
                if idf_dict[word] < idf_thr:
                    company_name = company_name.replace(word,"")

    return company_name

def productDict(pairsData):
    """
    transform the data into Dict with product info
    :param pairsData: (companyName,product)
    :return: dict={companyName:[product1,...]...}
    """
    product_dict = {}
    for company_name,product in pairsData:
        if company_name not in product_dict:
            product_dict[company_name] = []
        product_dict[company_name].append(product)
    return product_dict

# def corpNameExtractsInsert(company_names,product_dict,sub_len,seperate_word,idf_thr,idf_dict):
#     """
#     insert data with format(company_name with abbretrivate info and product,type--0:product exists 1:else,company_name,update_time--'%Y-%m-%d %H:%M:%S')
#     :param company_names: __iters__(company_name)
#     :param product_dict: dict input with product dict info
#     :param sub_len: substring length to be choosed
#     :param conn: connect mysql server
#     :return:
#     """
#     #name_extracts = []
#     conn = odbc_connect(host="118.89.139.154", port=11433, user="sa", db="CFB", passwd="somao@520", charset='utf8')
#     count = 0
#     for company_name in company_names:
#         assert type(company_name[0]) == str
#         #name_extract = corpNameExtract(company_name[0],sub_len)
#         # 多进程不能有全局变量
#         name_extract = extractNameDrop(company_name[0],seperate_word,idf_thr,idf_dict)
#         print("so far the name_extract={}".format(name_extract))
#         print("params:{},{},{},{}".format(company_name[0],seperate_word,idf_thr,idf_dict[seperate_word]))
#         if '有限公司' in name_extract:
#             break
#         if len(name_extract) < 4:
#             continue
#         #print("so far the name_extract={}".format(name_extract))
#         product_info = ""
#         if company_name[0] in product_dict:
#             product_info = ",".join(set(product_dict[company_name[0]]))
#         res = product_info
#         if name_extract not in product_info and len(product_info) > 0:
#             res = name_extract + "," + product_info
#         elif len(product_info) == 0:
#             res = name_extract
#         else:
#             pass
#         time_now = time.localtime()
#         update_time = time.strftime('%Y-%m-%d %H:%M:%S',time_now)
#
#         entity_type = 0
#         if not product_info:
#             entity_type = 1
#         count += 1
#
#         try:
#             #print("begain insert data and conn:")
#             cursor = conn.cursor()
#             cursor.execute("insert into abbr_and_product_all(entities,type,company_name,update_time)values('%s','%d','%s','%s')" %(res,entity_type,company_name[0],update_time))
#             conn.commit()
#             print("insert the {}(th) data successfully".format(count))
#         except Exception as e:
#             print("插入数据失败: ",e)


def multiThread(thread_num,name,data,worker,**kwargs):
    threads = []
    batch,reserve = divmod(len(data),thread_num)
    if reserve != 0:
        batch += 1
    for i in range(thread_num):
        thread_name = name + str(i)
        #print("thread_name: ",thread_name)
        try:
            if kwargs:
                thread = threading.Thread(target=worker,name=thread_name,args=(data[i*batch:(i+1)*batch],kwargs["product"],kwargs["sub_len"],kwargs["conn"]))
            else:
                thread = threading.Thread(target=worker, name=thread_name, args=(data[i * batch:(i + 1) * batch],))
            thread.start()
            threads.append(thread)
        except Exception as e:
            print("all data has been distribute over with error: ",e)
            break
    for thread in threads:

        thread.join()

def multiprocess(data,pNum,worker,**kwargs):
    dataNum=len(data)
    #print("dataNum length:",dataNum)
    dataEach=divmod(dataNum,pNum)[0]
    dataLast=divmod(dataNum,pNum)[1]
    pool=Pool()
    if dataLast!=0:
        dataEach=dataEach+1
    for i in range(pNum):
        try:
            if kwargs:
                pool.apply_async(worker,(data[i*dataEach:(i+1)*dataEach],kwargs["product"],kwargs["sub_len"],kwargs["seperate"],kwargs["idf_thr"],kwargs["idf_dict"]))
            else:
                pool.apply_async(worker,(data[i*dataEach:(i+1)*dataEach]),)
        except Exception as e:
            print("all data has been substribute on the Pools: ",e)
            break
    pool.close()
    pool.join()

def get_logger(log_file):
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sh.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger

if __name__ == '__main__':

    start = time.time()
    if os.path.exists('data/product_dict.pkl'):
        with open('data/product_dict.pkl','rb') as fr:
            product_dict = pickle.load(fr)
    else:
        connect_product = ["118.89.139.154", 20007, "root", "somao1129", "tianyancha"]
        mysql_conn = mysqlConnect(*connect_product)
        product_dict = {}
        try:
            cursor = mysql_conn.cursor()
            cursor.execute("select corp_name,brand_name from tianyancha_brand_detail")
            pairData = cursor.fetchall()
        except Exception as e:
            print("mysql can't connect: ",e)
        else:
            product_dict = productDict(pairData)
            with open('data/product_dict.pkl',mode='wb') as fw:
                pickle.dump(product_dict,fw)
        finally:
            if connect_product:
                cursor.close()
                mysql_conn.close()
    middle = time.time()
    #连接sqlServer,并插回数据
    
    conn = odbc_connect(host="118.89.139.154", port=11433, user="sa", db="CFB", passwd="somao@520", charset='utf8')
    try:
        cursor = conn.cursor()
        cursor.execute("select corp_name from dbo.result_cmpy_basic_info")
        pairData = cursor.fetchall()
        print("length of pairData={}".format(len(pairData)))
    except Exception as e:
        print(e)
    else:
        #open 20 threads to compute
        #kwargs = dict(product=product_dict,sub_len=5,conn=conn)
        #multiThread(20,'insertThread',pairData,corpNameExtractsInsert,**kwargs)
        if not os.path.exists('data/idf_companyName.pkl'):
            idf_dict = idfValue(pairData)
            with open('data/idf_companyName.pkl','wb') as fw:
                pickle.dump(idf_dict,fw)
        else:
            with open('data/idf_companyName.pkl','rb') as fr:
                idf_dict = pickle.load(fr)
        print("多进程任务插入数据")
        kwargs = dict(product=product_dict,sub_len=5,seperate_word='科技',idf_thr=6,idf_dict=idf_dict)
        multiprocess(pairData,20,corpNameExtractsInsert,**kwargs)
    finally:
        #print("close begain")
        if conn:
            cursor.close()
            conn.close()
    end = time.time()
    print("生成产品字典结果耗时:{}(min),插入结果表耗时:{}(min)".format(round((middle-start)/60),2),round((end-middle)/60,2))
    """
    #test abbretrivate function corpNameExtract
    conn = odbc_connect(host="118.89.139.154", port=11433, user="sa", db="CFB", passwd="somao@520", charset='utf8')
    try:
        cursor = conn.cursor()
        cursor.execute("select top 20 corp_name from dbo.result_cmpy_basic_info")
        pairData = cursor.fetchall()
    except Exception as e:
        print(e)
    else:
        rec = [str(x).zfill(2) for x in range(1,len(pairData)+1)]
        id = 0
        max_len = maxLen(pairData)
        for pair in pairData:

            abbr = corpNameExtract(pair[0],5)
            print("{}th record:{}{} ----> extract result={}".format(rec[id],pair[0]," "*(max_len-len(pair[0]))*2,abbr))
            id += 1
    finally:
        if conn:
            cursor.close()
            conn.close()
    """
