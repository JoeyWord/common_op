#!/usr/bin/env/py35
# coding=utf-8
import requests
import json
from urllib.request import urlopen,Request
from urllib.parse import urlencode
import ssl
from flask import Flask,jsonify,g,request
import logging
import os



API_KEY = 'aQRWZp00xQ4aX56D03gzuo7Y'
SECRET_KEY = 'Ip8ARjMQc1j6O3mgZNDNZQgAs3v0GBfn'
URL = 'https://aip.baidubce.com/oauth/2.0/token'

access_token = '24.78564510448a14b080beaf5ad16075ad.2592000.1543485064.282335-14130720'



app = Flask(__name__)

def get_log(log_path):

    logger = logging.getLogger(log_path)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


class BaiduAi():
    def __init__(self,app_key,app_secret,url,logger):
        self.app_key = app_key
        self.app_secret = app_secret
        self.url = url
        self.logger = logger
        #self.access_token = self.getAuth(self.url,self.app_key,self.app_secret)
        self.data = {}
        self.headers = {"content-type": "application/json; charset=UTF-8"}



    def setParams(self,data,key,value):
        data[key] = value
        return data
    def urlGen(self,host,data):
        url = host + '?'
        param_ls = []
        for key,value in data.items():
            param = str(key) + '=' + str(value)
            param_ls.append(param)
        params = '&'.join(param_ls)
        return url + params

    def getAuth(self,url,app_key,app_secret):
        params = {"grant_type":"client_credentials","client_id":app_key,"client_secret":app_secret}
        headers = {"content-type": "application/json; charset=UTF-8"}
        """
        r = requests.get(url,data=params,headers=headers)
        print(r.text)
        datas = json.loads(r.text)
        access_token = datas.get("access_token",None)
        """
        #pdb.set_trace()
        data = urlencode(params).encode('utf-8')
        req = Request(url,data=data,headers=headers,method='POST')
        #url_req = url + '?grant_type=client_credentials' + '&client_id=' + app_key + '&client_secret=' + app_secret
        #url_req = self.urlGen(url)
        #print('url_req result: ',url_req)
        #req = Request(url_req)
        #req.add_header("content-type","application/json; charset=UTF-8")
        content = urlopen(req).read().decode('utf-8')
        if not type(content) == str:
            self.logger.info('type change')
            content = str(content,encoding='utf-8')
        datas = json.loads(content)
        access_token = datas.get("access_token")
        self.logger.info("access_token result: {}".format(access_token))
        return access_token

    @staticmethod
    def requestRes(access_token,host,data,headers):
        data_js = json.dumps(data)
        info = host.split('/')[-1]
        if access_token:
            url = host + '?' + "access_token=" + access_token
            r = requests.post(url,data=data_js,headers=headers,timeout=15)
            r.encoding = "gbk"
            #print("\n{} request info:{}\n".format(info,r.text))
            return json.loads(r.text)
        else:
            print("access_token can't get successfully")
            return None
    #词义分析于短文本相似度评估
    def wordAnalysis(self,host,word1,word2):

        if len(word1) > 32 or len(word2)> 32:
            self.logger.debug("input info too long for word analysis")
            return "invalid input for word analysis"

        self.setParams(self.data,"word_1",word1)
        self.setParams(self.data,"word_2",word2)
        req = self.requestRes(access_token,host,self.data,self.headers)
        #self.logger.info("{} request info:{}".format("info1",req))
        self.data = {}
        return req

    def textSim(self,host,text1,text2,model='BOW'):
        if len(text1) > 256 or len(text2) > 256:
            self.logger.debug("input info too long for text sim")
            return "invalid input for text sim"

        self.setParams(self.data, "text_1", text1)
        self.setParams(self.data, "text_2", text2)
        self.setParams(self.data, "model", model)

        req = self.requestRes(access_token, host, self.data, self.headers)
        self.data = {}
        return req

    #评论点抽取
    def commentPoint(self,host,text,type=4):
        if len(text) > 5120:
            self.logger.debug("input info too long for comment point extract")
            return "invalid input for comment point"

        self.setParams(self.data,'text',text)
        self.setParams(self.data,'type',type)
        type_value = range(1,14)
        req = self.requestRes(access_token, host, self.data, self.headers)
        self.data = {}
        return req

    def emotionTrend(self,host,text):
        if len(text) > 1024:
            self.logger.debug("input info too long for emotion trend")
            return "invalid input for emotion trend"
        self.setParams(self.data,'text',text)
        req = self.requestRes(access_token, host, self.data, self.headers)
        self.data = {}
        return req

    def articleTags(self,host,title,content):
        if len(title) <= 40 and len(content) <= 32767:
            self.setParams(self.data,'title',title)
            self.setParams(self.data,'content',content)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for article tags"
        req = self.requestRes(access_token, host, self.data, self.headers)
        self.data = {}
        return req

    def topicClassify(self,host,title,content):
        if len(title) <= 40 and len(content) <= 32767:
            self.setParams(self.data,'title',title)
            self.setParams(self.data,'content',content)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for topic classify"
        req = self.requestRes(access_token, host, self.data, self.headers)
        self.data = {}
        return req

    def textCheck(self,host,text):
        if len(text) <= 10000:
            self.setParams(self.data,'content',text)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for text check"
        headers = {'content-type':'x-www-form-urlencoded'}
        info = host.split('/')[-1]
        url = host + "?" + "access_token=" + access_token
        req = requests.post(url,data=self.data,headers=headers,timeout=5)
        if not req.encoding:
            req.encoding = 'gbk'
        self.data = {}
        return req.text

    def word2vec(self,host,word):
        if len(word) <= 32:
            self.setParams(self.data,'word',word)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for word2vec"
        req = self.requestRes(access_token,host,self.data,self.headers)
        self.data = {}
        return req

    def DNNsequence(self,host,text):
        if len(text) <= 128:
            self.setParams(self.data,'text',text)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for DNNseq"
        req = self.requestRes(access_token,host,self.data,self.headers)
        self.data = {}
        return req

    #text check fault need privillage from work form
    def checkFault(self,host,text):
        if len(text) <= 255:
            self.setParams(self.data,'text',text)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for fault chek"
        req = self.requestRes(access_token,host,self.data,self.headers)
        self.data = {}
        return req
    def dependencyParsing(self,host,sentence,mode=0):
        if len(sentence) <= 128:
            self.setParams(self.data,'text',sentence)
            self.setParams(self.data,'mode',mode)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for denpendecy parsing"
        req = self.requestRes(access_token,host,self.data,self.headers)
        self.data = {}
        return req
    def wordAnalysisCommon(self,host,sentence):
        if len(sentence) <= 10000:
            self.setParams(self.data,'text',sentence)
        else:
            self.logger.debug("input length overpass the limit")
            return "invalid input info for word analysis common edition"
        req = self.requestRes(access_token,host,self.data,self.headers)
        self.data = {}
        return req


def get_response(res,name):
    response = {}
    status = 0

    if res and str(res).startswith("invalid"):
        status = 1
    elif not res:
        status = 2
    elif "error_code" in res:
        status = 3
        #print(type(res))
        if type(res) == dict:
            res.update({"status":status})
            return res
    response.update({name:res,'status':status})
    return response

if not os.path.exists('log'):
    os.makedirs('log')
logger = get_log(os.path.join('log','api_post.log'))

baiduAi = BaiduAi(API_KEY,SECRET_KEY,URL,logger)

@app.route('/nlp/<string:func_type>',methods=['POST'])
def somaoNLP(func_type):
    params = request.get_json()
    if func_type == "word_sim":
        logger.info("begain analyse the word mean")
        emb_sim_host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim"
        word_ls = ["word_1","word_2"]
        if all(word in params for word in word_ls):
            word_emb = baiduAi.wordAnalysis(emb_sim_host,params.get(word_ls[0]),params.get(word_ls[1]))
            response = get_response(word_emb,"word_emb_res")
            #logger.info("response result:{}".format(response))
            return jsonify(response),100
        else:
            return "invalid params input",101
    elif func_type == "text_sim":
        logger.info("begain text sim compute")
        text_sim_host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/simnet"
        text_ls = ["text_1","text_2"]
        if all(word in params for word in text_ls):
            text_sim = baiduAi.textSim(text_sim_host,params.get(text_ls[0]),params.get(text_ls[1]))
            response = get_response(text_sim,"text_sim_res")
            return jsonify(response),200
        else:
            return "invalid params input", 201
    elif func_type == "comment_point":
        logger.info("begain comment point extract")
        comment_point_host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/comment_tag"
        if "text" in params:
            comment_point = baiduAi.commentPoint(comment_point_host,params.get("text"))
            if "type" in params:
                comment_point = baiduAi.commentPoint(comment_point_host,params.get("text"),params.get("type"))
            response = get_response(comment_point,"comment_point_extract")
            return jsonify(response),300
        else:
            return "invalid params input", 301
    elif func_type == "sentiment_classify":
        logger.info("begain emotion trend analysis")
        emotion_trend_host = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify"
        if "text" in params:
            emotion_trend = baiduAi.emotionTrend(emotion_trend_host,params.get("text"))
            response = get_response(emotion_trend,"emotion_trend_result")
            return jsonify(response),400
        else:
            return "invalid params input", 401
    elif func_type == "article_tag":
        logger.info("begain tag extract")
        info = ['title','content']
        article_tag_host = "https://aip.baidubce.com/rpc/2.0/nlp/v1/keyword"
        if all(key in params for key in info):
            article_tag = baiduAi.articleTags(article_tag_host,params.get(info[0]),params.get(info[1]))
            response = get_response(article_tag,"article_tag_extract")
            return jsonify(response),500
        else:
            return "invalid params input", 501
    elif func_type == "article_classify":
        logger.info("begain article classify")
        info = ['title','content']
        article_classify_host = "https://aip.baidubce.com/rpc/2.0/nlp/v1/topic"
        if all(key in params for key in info):
            article_classify = baiduAi.articleTags(article_classify_host,params.get(info[0]),params.get(info[1]))
            response = get_response(article_classify,"article_classify_res")
            return jsonify(response),600
        else:
            return "invalid params input", 601
    elif func_type == "text_check":
        logger.info("begain text check")
        text_check_host = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam'
        if "text" in params:
            text_check = baiduAi.textCheck(text_check_host,params.get('text'))
            response = get_response(text_check,"text_check_res")
            return jsonify(response),700
        else:
            return "invalid params input", 701
    elif func_type == "word2vec":
        logger.info("begain transform word to vector")
        word_vector_host = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_vec'
        if "word" in params:
            word2vec = baiduAi.word2vec(word_vector_host,params.get("word"))
            response = get_response(word2vec,"word2vec_res")
            return jsonify(response),800
        else:
            return "invalid params input", 801
    elif func_type == "wordAnalysisCommon":
        logger.info("begain word analysis(contain word tokens and segment symbol) from sentence")
        word_analysis_host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer'
        if "text" in params:
            wordAna = baiduAi.wordAnalysisCommon(word_analysis_host,params.get("text"))
            response = get_response(wordAna,"wordAnalysis_res")
            return jsonify(response),900
        else:
            return "invalid params input", 901

    elif func_type == "dependency_parsing":
        logger.info("begain syntax dependency parse")
        dependency_parsing_host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/depparser'
        if "sentence" in params:
            dependency_parse = baiduAi.dependencyParsing(dependency_parsing_host,params.get("sentence"))
            if "mode" in params:
                dependency_parse = baiduAi.dependencyParsing(dependency_parsing_host, params.get("sentence"),params.get("mode"))
            response = get_response(dependency_parse,"dependency_parse_res")
            logger.info("dependency parse: {}".format(response))
            return jsonify(response),1000
        else:
            return "invalid params input", 1001

    elif func_type == "check_fault":
        logger.info("begain check the word appear place right or not")
        check_fault_host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/ecnet'
        if "text" in params:
            check_faulting = baiduAi.checkFault(check_fault_host,params.get("text"))
            response = get_response(check_faulting,"check_fault_res")
            logger.info("check fault: {}".format(response))
            return jsonify(response),1100
        else:
            return "invalid params input", 1101
    elif func_type == "DNNsequence":
        logger.info("begain analyse the word prob from sequnce text")
        DNN_seq_host = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/dnnlm_cn'
        if "text" in params:
            seq_prob = baiduAi.DNNsequence(DNN_seq_host,params.get("text"))
            response = get_response(seq_prob,"seq_prob_res")
            logger.info("DNN result:{}".format(response))
            return jsonify(response),1200
        else:
            return "invalid params input", 1201

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=5000)

    '''
    baiduAi = BaiduAi(API_KEY,SECRET_KEY,URL,logger)
    #词义识别
    word1 = "栋梁"
    word2 = "北京"
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim"
    baiduAi.wordAnalysis(host,word1,word2)
    #文本相似识别
    text1 = '海阔凭鱼跃'
    text2 = '天高任鸟飞'
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/simnet"
    baiduAi.textSim(host,text1,text2,model='BOW')
    #评论点抽取
    text = "三星电脑电池不给力"
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/comment_tag"
    baiduAi.commentPoint(host,text)
    #情感倾向分析
    text = "这是一次伟大的尝试"
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify"nlp
    baiduAi.emotionTrend(host,text)
    #标签提取
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v1/keyword"
    title = '隐形的翅膀'
    comment = '每一次都在徘徊中坚强，每一次就算很受伤也会有泪光，我知道我一直有双隐形的翅膀，带我飞向更远的地方'
    baiduAi.articleTags(host,title,comment)
    #文章分类
    host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/topic'
    baiduAi.topicClassify(host,title,comment)
    #文本审核
    text = '老吾老以及人之老，幼吾幼以及人之幼'
    host = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam'
    baiduAi.textCheck(host,text)
    '''
