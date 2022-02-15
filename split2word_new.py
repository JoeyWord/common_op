#!/usr/bin/env/py35
# coding=utf-8
import jieba

entity_pos = ["nz","nt","nrt"]


def split2word_new(file2read,file2write):
    file_write = open(file2write,mode='w',encoding='utf-8')
    with open(file2read,mode='r',encoding='utf-8') as fr:
        count = 0
        for line in fr.readlines():
            count += 1
            if not line:
                continue
            elif line.startswith('-DOC'):
                if count > 1:
                    file_write.write('\n')
            else:
                items = line.split()
                #print('line info:',line)
                if len(items) != 2:
                    continue
                segs = jieba.cut(items[0])
                for word in segs:
                    word_len = len(word)
                    #print("word info:",word)
                    i = 0
                    while(i < word_len):
                        if not items[1].startswith('O') and i >= 1:
                            file_write.write(word[i] + " " + 'I-' + items[1].split('-')[1])
                            file_write.write('\n')
                        else:
                            file_write.write(word[i] + " " + items[1])
                            file_write.write('\n')
                        i += 1


if __name__ == '__main__':
    """
    corpus_choose = "title"
    connectInfo=["118.89.139.154",20009,"root","somao1129","news"]
    conn=sqlConnect(*connectInfo)
    cursor=conn.cursor()
    if corpus_choose == "text":
        cursor.execute("select text from 36kr_detail limit 10")
    else:
        cursor.execute("select title from 36kr_detail limit 10000")
    corpusData=cursor.fetchall()
    print("corpusData length={}".format(len(corpusData)))
    if conn:
        cursor.close()
        conn.close()
    tokens_with_IBtags_new(corpusData,0)
    """
    split2word_new('data/corpus_title_0.txt','data/title_input.txt')
