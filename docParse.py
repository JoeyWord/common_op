# coding=utf-8
from bs4 import BeautifulSoup
import re

def unstandard_count(soup,tag_name,tag,standard_format):
    subjects=soup.select(tag_name)
    print("length subs info: ",len(subjects))
    sum_all = 0
    for sub in subjects:
        tags=sub.find_all(tag)
        style_tag=sub.find_all(tag,{"style":re.compile(standard_format)})
        print("subs length:{} and length style_tag:{}".format(len(tags),len(style_tag)))
        tag_standards=len(style_tag)
        sum_all+= len(tags)-tag_standards
    print("在查找到的标签范围内不匹配的值为:",sum_all)
#unstandard_count(html,"table","col",col_style)
    


#check levels title
def unstandard_title(soup,tag_name,child_tag,levels,standard_format_num,standard_format_char,standard_format_num2=None):
    subjects=soup.select('%s[class="%d a DocDefaults "]' %(tag_name,levels))
    print("{} level title select nums: {}".format(levels,len(subjects)))
    total_items = 0
    cur_level_num = 0
    cur_level_char = 0
    for sub in subjects:
        sub_tags = sub.select(child_tag)
        total_items += len(sub_tags)
        child_tag_nums=sub.find_all(child_tag,{"style":re.compile(standard_format_num)})
        if levels > 1:
            standard_format_num2 = highLevel_num_format
            child_tag_nums2 = sub.find_all(child_tag,{"style":re.compile(standard_format_num2)})
        for child_tag_num in child_tag_nums:
            if len(re.sub('\w','',child_tag_num.text))<=1:
                cur_level_num += 1
        for child_tag_num in child_tag_nums2:
            if len(re.sub('\w','',child_tag_num.text))<len(child_tag_num.text):
                cur_level_num += 1
        child_tag_chars = sub.find_all(child_tag,{"style":standard_format_char})
        for _ in child_tag_chars:
            cur_level_char += 1
        
        #print("match the length:{} and length style_tag:{}".format(len(tags),len(style_tag)))
        #tag_standards=len(style_tag)
        #sum_all+= len(tags)-tag_standards
    non_match_items = total_items - cur_level_char - cur_level_num
    print("当前标题级别{}--总的查找条目:{},在查找到的标签范围内不匹配的值为:{}".format(levels,total_items,non_match_items))
    #return subjects


"""
#check table font 
span_info=[];ss_info=[]
style_info = re.compile('color: #000000;font-size: 11.0pt;;font-family: "SimSun";')
pattern = re.compile(".*color.")
style_info = 'color'
count = 0;count_style=0
td_style = "background-color: #FFC000;border-bottom-style: \
            solid;border-bottom-width: 1px;border-bottom-color: \
            #000000;border-left-style: solid;border-left-width: \
            1px;border-left-color: #000000;border-right-style: \
            solid;border-right-width: 1px;border-right-color: \
            #000000;border-top-style: solid;border-top-width: \
            1px;border-top-color: #000000;vertical-align: bottom;"
col_style = "width: 13.85%;"
tr_style = "height: 0.19in;"


sum_all = 0
#check col style:width,#check tr standard
tables = html.select('table[id^="docx4j"]')
print("length table",len(tables))
for table in tables:
    childs = table.colgroup.children
    style_col = table.find_all("col",{"style":re.compile("width: 13.85%;")})
    print("length style_col:",len(style_col))
    col_standards = len(style_col)
    #print("childs",childs)
    col_nums = 0
    for child in childs:
        col_nums += 1
    print("col_standard={} and col_nums={}".format(col_standard,col_nums))
    sum_all += col_nums-col_standards
print("all tables non-standard col numbers: ",sum_all)    


#check td font-size
for table in table_info:
    table_style = table.select('[id^="docx4j"]')
    table_style = table.find({"id":re.compile('^docx4j')})
    if table_style:
        count += 1
        td_style = table_style.find({"style":td_style})
        print("td_style",td_style)
        col_style = table_style.find(style=col_style)
        print("col_style",col_style)
        tr_style = table_style.find(attrs={"style":tr_style})
        print("tr_style",tr_style)
        if td_style and col_style and tr_style:
            count_style += 1
    spans = table.find_all('span')
    spans_standards = table.find_all('span',attrs={"style":re.compile('font-size: 11.0pt;;font-family: ')})
    #print(spans[0])
    for span in spans:
        span_info.append(span.text)
    
    for ss in spans_standards:
        ss_info.append(ss.text)
print("count={},count_style={} and span_info length={},span_style length={}".format(count,count_style,len(span_info),len(ss_info)))
non_standards = count-count_style + len(span_info) - len(ss_info)
print("表格式不符合规范的记录数：",non_standards)
"""
if __name__ == "__main__":
    #check title
    loc_format = "text-align: center;margin-top: 5mm;margin-bottom: 0.43in;"
    title_font = "font-weight: bold;font-size: 16.0pt;"
    html = BeautifulSoup(open('data/doc2html.html','r',encoding='utf-8'),'lxml')
    title_tag = html.find("p")
    standard_title_loc = html.find(attrs={"style":loc_format})
    count_title = False
    if standard_title_loc:
        standard_title = standard_title_loc.find("span",{"style":title_font})
        if standard_title:
            count_title = True
            print("the title match the standard")
    #levels title check
    title_char_format = "font-size: 12.0pt;"
    title_num_format = "font-size: 12.0pt;;font-family: 'Calibri';"
    highLevel_num_format = "font-size: 12.0pt;;font-family: 'Cambria';white-space:pre-wrap;"
    unstandard_title(html,"p","span",2,title_num_format,title_char_format)
