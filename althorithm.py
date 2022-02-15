#!/usr/bin/env/py35
# coding=utf-8

class TrieTree():
    """
    define trie tree attribute
    """
    def __init__(self):
        self.isTerminalNode = True
        self.num = 1
        self.subNodes = [None]*7000
        self.char = ''

class TrieConstruct():
    def __init__(self):
        self.trie = TrieTree()

    def _insert(self,word):
        if not word:
            return
        i=0
        trie = self.trie
        while i<len(word):
            pos=divmod(ord(word[i])-ord(u'\u4e00'),7000)[-1]
            if not trie.subNodes[pos]:
                trie.subNodes[pos] = TrieTree()
                trie.char = word[i]
            else:
                trie.num += 1
            trie = trie.subNodes[pos]
            i += 1
        trie.isTerminalNode = True


    def _match_word(self,word):
        if not word:
            return False
        i=0
        trie = self.trie
        while i<len(word):
            pos = divmod(ord(word[i])-ord(u'\u4e00'),7000)[-1]
            if not trie.subNodes[pos]:
                return False
            else:
                trie = trie.subNodes[pos]
            i += 1
        return trie.isTerminalNode

    def _compute_prefix(self,word):
        if not word:
            return 0
        trie = self.trie
        i=0
        while i<len(word):
            pos = divmod(ord(word[i])-ord(u'\u4e00'),7000)[-1]
            if not trie.subNodes[pos]:
                return 0
            else:
                trie = trie.subNodes[pos]
            i += 1
        return trie.num

if __name__ == '__main__':
    import time

    insert_dd={"你好啊","看着真不错",'看起来还可以','不好说',"还可以"}
    test_ls = ["你好","不错","不好说","还可以"]
    trieTree = TrieConstruct()
    t0=time.time()
    for _dd in insert_dd:
        trieTree._insert(_dd)
    t1 = time.time()
    print("trie construct success and cost time:%.2f" %(t1-t0))
    prefix = "看着"
    i = 1
    prefix_dd = {}
    while i<len(prefix)+1:
        if prefix[:i] not in prefix_dd:
            prefix_dd[prefix[:i]] = 0
        prefix_dd[prefix[:i]] += trieTree._compute_prefix(prefix[:i])
        i += 1
    t2 = time.time()
    print("compute prefix cost time:{} \n prefix dict info:{}".format((t2-t1),prefix_dd))
    word_freq = {}
    for _t in test_ls:
        match_flag = trieTree._match_word(_t)
        if _t not in word_freq:
            word_freq[_t] = 0
        if match_flag:
            word_freq[_t] += 1
    t3=time.time()
    print("search the match word cost time: %.2f" %(t3-t2))
    for _k,_v in word_freq.items():
        if _v == 0:
            print("word %s not in trie" %_k)
        else:
            print("word %s in trie with freq= %d" %(_k,_v))





