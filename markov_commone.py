#!/usr/bin/env/py35
# coding=utf-8
from random import randint
#from string import punctuation
from urllib.request import urlopen

def wordListSum(wordList):
    s = 0
    for word,value in wordList.items():
        s += value
    return s

def retrieveRandomWord(wordList):
    randIndex = randint(1,wordListSum(wordList))
    for word,value in wordList.items():
        randIndex -= value
        if randIndex <= 0:
            return word
        else:
            return ""

def cleanText(text):
    text = text.strip()
    text = text.replace('“','')
    text = text.replace('”','')
    text = text.replace('\n','')
    return text

def buildWordDict(text):
    text = cleanText(text)

    wordDict = {}
    punctuation = ['.','?','!',':']
    for s in punctuation:
        text=text.replace(s,"" + s + " ")
    words = [word for word in text.split() if word != ""]
    for i,word in enumerate(words):
        if word not in wordDict:
            wordDict[word]={}
            if words[i+1] not in wordDict[word]:
                wordDict[word][words[i+1]] = 0
            wordDict[word][words[i+1]] += 1
    return wordDict

if __name__ == '__main__':
   text_url='http://pythonscraping.com/files/inaugurationSpeech.txt'
   text = str(urlopen(text_url).read(),encoding='utf-8')
   wordDict = buildWordDict(text)
   cur_word = 'I'
   i = 0
   markolvChain = cur_word
   while i<100:
        if cur_word in wordDict:
            markolvChain += " " + retrieveRandomWord(wordDict[cur_word])
            cur_word = retrieveRandomWord(wordDict[cur_word])
        else:
            raise ValueError("no value in dict")
        print("markolvChain result:\n",markolvChain)




