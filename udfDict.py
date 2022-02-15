# !/usr/bin/python3
# -*- coding:utf-8 -*-


from entity_commonFun_jin import odbc_connect
import re
import jieba.posseg as pseg
import pickle

entity_pos=["nz","nt","nrt","n"]

with open('data/idf_companyName.pkl','rb') as fr:
	idf_dict = pickle.load(fr)

def write2udfDic(filename,conn):
	file_write = open(filename,mode='w',encoding='utf-8')
	try:
		cursor = conn.cursor()
		sql = """
				select entities from dbo.abbr_and_product_all 
				where entities not like '%股份%' and entities not like '%保定%' 
				"""
		cursor.execute(sql)
		pairsData = cursor.fetchall()
	except Exception as e:
		print("throw read table fail:",e)
	else:
		word_dic = {}
		for pair in pairsData:
			#print("pair[0]: ",pair[0])
			assert '股份' not in pair[0]
			items = pair[0].split(',')
			word_count = 0
			for word in items:
				word_count += 1
				word = word.replace(' ', '')
				sub_word = re.sub('\W+','',word)
				if len(sub_word) < len(word):
					continue
				sub_word = re.sub('\s+','',word)
				if len(sub_word) < len(word):
					continue
				sub_word = re.sub('[a-zA-Z0-9_]','',word)
				if len(sub_word) < len(word):
					continue

				segs = pseg.cut(word)
				new_word = ''
				for w,p in segs:
					if p in entity_pos and w in idf_dict and len(w) >= 2:
						if idf_dict[w] > 50:
							new_word += w
							if len(new_word) > 4:
								break
				if len(new_word) >= 2:
					if new_word not in word_dic:
						word_dic[new_word] = 0
					word_dic[new_word] += 1

		for word in word_dic:
			#print("word result={}".format(word))
			freq = word_dic[word] + 10
			line = word + " " + str(freq) +" " + 'nz'
			file_write.write(line)
			file_write.write('\n')
		print("file sucessfully write into")
	finally:
		if file_write:
			file_write.close()
		if conn:
			cursor.close()
			conn.close()

if __name__ == '__main__':
	conn = odbc_connect(host="118.89.139.154", port=11433, user="sa", db="CFB", passwd="somao@520", charset='utf8')
	write2udfDic('data/udfDic.txt',conn)

