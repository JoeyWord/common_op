#!/usr/bin/env/py35
# coding=utf-8
#from pylab import plt
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def file2dict(file):
    entity_dict = {}
    with open(file,mode='r') as fr:
        for line in fr.readlines():
            try:
                entity,word = line.split()
            except:
                print("no enough words to unpack")
            else:
                if entity not in entity_dict:
                    entity_dict[entity] = []
                entity_dict[entity].append(word)
    return entity_dict


def graph(res,res_comp,font_size,fig_size,bar_width):
    """
    graph the result of predict for NER,
    :param font_size: int
    :param fig_size: tuple(width,height)
    :param bar_width: int--bar width
    :param res: dict for( org,loc,per) with format:dict(keyword:word,value:[])
    :return:
    """
    #figure = plt.figure(figsize=(15,10))
    #ax1 = figure.add_subplot(1,2,1)
    #ax2 = figure.add_subplot(1,2,2)
    entity_count = {}
    for word in res:
        count = len(res[word])
        entity_count[word] = count
    print("entity_count:",entity_count)

    keys = list(entity_count.keys())

    entity_compare = {}
    for word in keys:
        count = len(res_comp[word])
        entity_compare[word] = count
    print("entity_compare:",entity_compare)


    #index = list(range(3))
    #index = [float(i) + 0.4 for i in index]
    #plt.ylim(0,70)
    #plt.xticks(index,keys)
    #plt.ylabel("count of entity")
    #rects = plt.bar(range(len(entity_count)),entity_count.values(),color='rgb')
    #for rect in rects:
    #    height = rect.get_height()
    #    plt.text((rect.get_x()+rect.get_width()/2),height,str(height) + '个数',ha='center',va='bottom')
    #plt.show()

    #compare plot
    #mpl.use('Agg')
    font_prop = mpl.font_manager.FontProperties(fname='font_prop/SIMSUN.TTC')
    mpl.rcParams['font.size'] = font_size
    mpl.rcParams['figure.figsize'] = fig_size
    mpl.rcParams['legend.edgecolor'] = 'b'
    mpl.rcParams['axes.grid'] = 'True'
    mpl.rcParams['axes.grid.axis'] = 'y'
    mpl.rcParams['grid.linestyle'] = '--'
    mpl.rcParams['grid.color'] = 'grey'
    #plt.rcParams['font.sans-serif'] = ['SemHei']
    #plt.rcParams['axes.unicode_minus'] = False

    names = [u'改进前',u'改进后']
    plt.title(u'改进前后对比',fontproperties=font_prop)
    index = np.arange(len(res))
    plt.ylim(ymin=0,ymax=50)
    plt.ylabel('count of entity')
    #plt.hlines(y=list(range(0,50,10)),xmin=-1,xmax=3,colors='grey',linestyles='--')
    subjects = tuple(keys)
    plt.xticks(index+bar_width/4,keys,fontproperties = font_prop)
    def add_text(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text((rect.get_x()+rect.get_width()/2),height,str(height) + u'个数',horizontalalignment='center',verticalalignment='bottom',fontproperties=font_prop)

    rect1 = plt.bar(index,entity_count.values(),bar_width/2,color='#0072BC',label=names[0])
    rect2 = plt.bar(index+bar_width/2,entity_compare.values(),bar_width/2,color='#ED1C24',label=names[1])
    plt.legend(loc='upper right', bbox_to_anchor=(1, 1), prop=font_prop,fancybox=True,facecolor='y')   #bbox_to_ahchor:图例的坐标位置(占比的形式)
    add_text(rect1)
    add_text(rect2)

    plt.show()
    plt.savefig('graph/entity_compare.jpg')


if __name__ == '__main__':

    res = file2dict('/usr/nlp/ner/ChineseNER-master/test/entity_result.txt')
    res_comp = file2dict('/usr/nlp/ner/ChineseNER-master/test/entity_result_new.txt')
    font_size = 10
    fig_size = (8,6)
    graph(res,res_comp,font_size,fig_size,0.5)


