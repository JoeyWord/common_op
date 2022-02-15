#!/usr/bin/env/py35
# coding=utf-8
import pymysql
from jieba import posseg
import jieba
from multiprocessing import Pool
import time
import re
import argparse
import traceback
#添加自定义公司名称语料
import numpy as np
import csv
import pandas as pd

entity_pos=["nz","nt","nrt"]
sentence_symbol = ["。", "？", "！","；"]

def freqSuggest(fileName,inputFile):
    word_freq = open(inputFile,mode='w',encoding='utf-8')
    with open(fileName,'r') as fr:
        for line in fr.readlines():
            items = line.split()
            assert len(items)==3
            freq = jieba.suggest_freq(items[0],True)
            word_freq.write(items[0] + ' ' + str(freq) + ' ' + items[-1])
            word_freq.write('\n')
    word_freq.close()

def sqlConnect(host,port,user,password,db,charset='utf8'):
    connectDict=dict(host=host,port=port,user=user,password=password,db=db,charset=charset)
    try:
        conn=pymysql.connect(**connectDict)
    except Exception as e:
        print(e)
        return None
    return conn

def clean_text(text):
    """
        @params: input string format text
        @return: string text with no symbol
    """
    content = re.sub("\s+","",text)
    #content = re.sub('\W+',"",content)
    #print(content)
    return content

def tokenize(sentence):
    sentence=clean_text(sentence)
    tokens=jieba.cut(sentence,HMM=True)
    for token in tokens:
        yield token

def tokens_with_IBtags_new(sentences,id):
    with open('data/corpus_title_' + str(id) + '.txt', mode='w', encoding='utf-8') as fw:
        for sentence in sentences:
            input_sen = sentence[0].replace('_36氪','')
            input_sen = input_sen.replace(' ','')
            input_sen = input_sen.replace('|','')
            segs = posseg.cut(input_sen)
            fw.write('-DOCSTART-')
            fw.write('\n')
            #near_pair = {}
            #print("test near_pair length",len(near_pair))
            for i,seg in enumerate(segs):
                if seg.flag in entity_pos:
                    seg.flag = "B-ORG"
                elif seg.flag == 'nr':
                    seg.flag = "B-PER"
                elif seg.flag == 'ns':
                    seg.flag = "B-LOC"
                else:
                    seg.flag = "O"
                line = seg.word + " " + seg.flag
                fw.write(line)
                fw.write('\n')


def tokens_with_IBtags(sentences,id):
    with open('data/corpus_title_' + str(id) + '.txt',mode='w',encoding='utf-8') as fw:
        for sentence in sentences:
            input_sen = sentence[0].replace('_36氪','')
            input_sen = input_sen.replace(' ','')
            input_sen = input_sen.replace('|','')
            segs = posseg.cut(input_sen)
            fw.write('-DOCSTART-')
            fw.write('\n')
            near_pair = {}
            #print("test near_pair length",len(near_pair))
            for i,seg in enumerate(segs):
                near_pair.update({i:seg.word})
                #print("near_pair={}".format(near_pair))
                if seg.flag in entity_pos:
                    seg.flag = "I-ORG"
                    if sentence[0].startswith(seg.word):
                        seg.flag="B-ORG"
                    elif len(near_pair)==2 and near_pair[i-1] in sentence_symbol:
                        seg.flag='B-ORG'

                elif seg.flag=='nr':
                    seg.flag="I-PER"
                    if sentence[0].startswith(seg.word):
                        seg.flag="B-PER"
                    elif len(near_pair)==2 and near_pair[i-1] in sentence_symbol:
                        seg.flag='B-PER'
                elif seg.flag=='ns':
                    seg.flag='I-LOC'
                    if sentence[0].startswith(seg.word):
                        seg.flag="B-LOC"
                    elif len(near_pair)==2 and near_pair[i-1] in sentence_symbol:
                        seg.flag='B-LOC'
                else:
                    seg.flag="O"
                line = seg.word + " " +seg.flag
                fw.write(line)
                fw.write('\n')
                if i>=2:
                    near_pair.pop(i-2)


#传入词信息预料的长度line number of file:383793
def split2word(file,write2file):
    fw = open(write2file,mode='w',encoding='utf-8')
    count = 0
    with open(file, mode='r', encoding='utf-8') as fr:
        for line in fr.readlines():
            count += 1
            if count == 1:
                continue
            try:
                word,tag=line.split()
            except Exception as e:
                #fw.write('\n')
                print("line info:", line, " error info:", e)
                if line.startswith('-DOC'):
                    fw.write('\n')
                #print("no more upack",e)
            else:
                if not word:
                    continue
                if len(word) == 1:
                    wl=word + " " +tag
                    fw.write(wl)
                    fw.write('\n')
                else:
                    assert len(word) > 1
                    new_word='|'.join(word)
                    for word in new_word.split('|'):
                        wl=word + " " + tag
                        fw.write(wl)
                        fw.write('\n')
    fw.close()
    print("传入词信息预料的长度={}".format(count))

def tokens_with_tags(sentences,id):
    with open('/usr/nlp/ner/corpus_' + str(id) + '.txt',mode='w') as fw:
        for sentence in sentences:
            segs = posseg.cut(sentence[0])
            fw.write('-DOCSTART-')
            fw.write('\n')
            for seg in segs:
                if seg.flag in entity_pos:
                    seg.flag="ORG"
                elif seg.flag=='nr':
                    seg.flag="PER"
                elif seg.flag=='ns':
                    seg.flag='LOC'
                else:
                    seg.flag="O"
                line = seg.word + " " +seg.flag
                fw.write(line)
                fw.write('\n')

def multiprocess(data,pNum,worker):
    dataNum=len(data)
    #print("dataNum length:",dataNum)
    dataEach=divmod(dataNum,pNum)[0]
    dataLast=divmod(dataNum,pNum)[1]
    pool=Pool()
    if dataLast!=0:
        dataEach=dataEach+1
    for i in range(pNum):
        try:
            pool.apply_async(worker,(data[i*dataEach:(i+1)*dataEach],(i+1),))
        except:
            pool.apply_async(worker,(data[i*dataEach:],(i+1)))
            break
    pool.close()
    pool.join()

def random_choose(file,file2write,size=100):
    if file.split('.')[-1] == 'txt':
        write_file = open(file2write,'w')
        index = 0
        with open(file,'r') as fr:
            lines = fr.readlines()
            random_arr = np.random.randint(0, len(lines), size=size)
            count_line = 0
            for ele in random_arr:
                if count_line < size-1:
                    write_file.write(lines[ele])
                else:
                    write_file.write(lines[ele])
                count_line += 1
    elif file.split('.')[-1] == 'csv':

        read_file = list(csv.reader(open(file,'r')))
        write_file = csv.writer(open(file2write,'w',newline=''))
        random_arr = np.random.randint(0, len(read_file), size=size)
        for ele in random_arr:
            write_file.writerow(read_file[ele])


def merge_data(file1,file2):
    if file1.split(',')[-1] == 'csv':
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        df_merge = pd.merge(df1,df2,how='inner',on=['title'])


if __name__ == '__main__':

    # generate corpus
    
    corpus_choose = "text"
    connectInfo=["118.89.139.154",20009,"root","somao1129","news"]
    conn=sqlConnect(*connectInfo)
    cursor=conn.cursor()
    if corpus_choose == "text":
        cursor.execute("select text from 36kr_detail limit 10")
    else:
        cursor.execute("select title,text from 36kr_detail limit 10000,3000")
    corpusData=cursor.fetchall()
    with open('data/title_test.txt',mode='w',encoding='utf-8') as fw:
        for pair in corpusData:
            line = pair[0].replace(' ','')
            line = line.replace('_36氪','')
            line = line.replace('|','')
            line = re.sub('\s+','',line)
            #text = re.sub('\s+','',pair[1])
            fw.write(line)
            fw.write('\n')
    print("corpusData length={}".format(len(corpusData)))
    if conn:
        cursor.close()
        conn.close()
    '''
    time_start=time.time()
    #freqSuggest('data/udfDic.txt','data/udf_word_freq.txt')

    jieba.load_userdict("data/udfDic.txt")
    try:
        tokens_with_IBtags_new(corpusData,0)
        #tokens_with_IBtags(corpusData,0)
        #multiprocess(corpusData,20,tokens_with_IBtags)
        #split2word('data/corpus_title_0.txt','data/title_input.txt')
    except Exception as e:
        print("多进程创建失败",e)
        print(traceback.format_exc(1))
    print("多进程插入数据完成")
    
    parser=argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='the file to be read', required=True)
    parser.add_argument('--write2file', type=str, help='the file to be write', required=True)
    args = parser.parse_args()
    time_start=time.time()
    split2word(args.file,args.write2file)
    time_end=time.time()
    print("time cost to generate word tag result: {}min".format(round((time_end-time_start)/60),3))
    '''
