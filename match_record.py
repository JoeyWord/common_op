#!/usr/bin/env/py35
# coding=utf-8
import csv
from entity_commonFun_jin import odbc_connect

def matchCompany(company_info,word):
    #match_comp = []
    for company in company_info:
        for key in company:
            tmp = company[key]
            if word in tmp[0]:
                print('the current word:',word)
                if (tmp[1] == 0 and word in tmp[0].split(',')[0]) or tmp[1] == 1:
                    match_level = 3
                    yield company,match_level,tmp[2]
                else:
                    match_level = 2
                    yield company,match_level,tmp[2]
            elif word in key:
                match_level = 1
                print('level 1 word: ',word)
                yield company,match_level,tmp[2]



def matchTestTitleComp(company_info,title_data_file,write2file):
    csv_reader = csv.reader(open(title_data_file,'r',encoding='utf-8'))
    count = 0
    csv_res = csv.writer(open(write2file,'a',newline=''))
    #csv_res.writerow(['id','title','entity_res','entity_res_new','entity_extract','company_match'])
    for item in csv_reader:
        count += 1
        if count>1:
            entities = item[-2].split('; ')
            print('the count ={} current entities:{}'.format(count,entities))
            line2write = [item[i] for i in range(len(item))]
            company_dict = {}
            for entity in entities:
                try:
                    word,entity_type,start_idx = entity.split('--')
                except Exception as e:
                    print(e," 当前行entity: ",entity)
                else:
                    match_comp_res = []
                    if entity_type == 'ORG':
                        nearest_loc = searchNearLoc(start_idx,entities)
                        print("the current entity:{} and nearest_loc:{}".format(entity,nearest_loc))
                        word_match = matchCompany(company_info,word)

                        #match_comp_res = []
                        for company,match_level,loc in word_match:
                            print("the current count={},company:{},match_level:{},loc:{}".format(count,company,match_level,loc))
                            if loc == nearest_loc:
                                match_level += 1
                                print("the current company match_level: ",match_level)
                            if company not in company_dict:
                                company_dict[company] = 0
                            company_dict[company] += match_level
                            #line = company + ': ' + str(match_level)
                            match_comp_res.append([company,match_level])
            match_sort = sorted(company_dict.items(),key=lambda kv:kv[1],reverse=True)
            match_res = []
            for company,match_level in match_sort:

                match_res.append(company + ': ' + str(match_level))
            line2write.append('; '.join(match_res))
            csv_res.writerow(line2write)

def searchNearLoc(start_idx,entities):
    nearest_loc = ''
    tmp_idx = 0
    for entity in entities:
        entity_word,entity_type,entity_idx = entity.split('--')
        if entity_type == 'LOC' and int(entity_idx) < int(start_idx):
            if int(entity_idx) >= int(tmp_idx):
                tmp_idx = int(entity_idx)
                nearest_loc = entity_word
    return nearest_loc

def companyInfoDict(pairData):
    for pair in pairData:
        yield {pair[2]:[pair[0],pair[1],pair[-1]]}

if __name__ == '__main__':

    conn = odbc_connect(host="118.89.139.154", port=11433, user="sa", db="CFB", passwd="somao@520", charset='utf8')
    try:
        cursor = conn.cursor()
    except Exception as e:
        print(e)
    else:
        cursor.execute("select top 1000 entities,type,company_name,location from dbo.abbr_and_product_all_LOC")
        pairData = cursor.fetchall()
        companyInfo = companyInfoDict(pairData)
        matchTestTitleComp(companyInfo,'/usr/nlp/ner/ChineseNER-master/data/title_test_res.csv','data/org_match_company.csv')
    finally:
        if conn:
            cursor.close()
            conn.close()

