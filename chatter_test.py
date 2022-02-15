#!/usr/bin/env/py35
# coding=utf-8

import time
from chatterbot.chatterbot import ChatBot
from chatterbot.trainers import ListTrainer,ChatterBotCorpusTrainer

CHATTERBOT_SETTING={
    'name': 'ChatterBot',
    'trainer': 'chatterbot.trainers.ChatterBotCorpusTrainer',
    'training_data': [
         'chatterbot.corpus.chinese'
    ]
}
chatter_bot = ChatBot(**CHATTERBOT_SETTING)

def test_chatter_list(list):
    chatter_bot.set_trainer(ListTrainer)
    chatter_bot.train(list)
    while True:
        try:
            input_sentence = input("user:")
            result = chatter_bot.get_response(input_sentence)
            print("chatterbot:",result)
        except(KeyboardInterrupt,RuntimeError,EOFError):
            break
def test_chatter_corpus():
    t_s = time.time()
    #chatter_bot.set_trainer(ChatterBotCorpusTrainer)
    chatter_bot.train(chatter_bot.training_data[0])
    t_e = time.time()
    print("train corpus cost time: %.2f(s)" %(t_e-t_s))
    while True:
        try:
            input_sentence = input("user:")
            t0 = time.time()
            print("bot:",chatter_bot.get_response(input_sentence))
            t1 = time.time()
            print("bot cost time:",(t1-t0))
        except(KeyboardInterrupt,RuntimeError):
            break

if __name__ == '__main__':
    list = ["今天天气不错","适合打球","那下午搞起","至少也得大战３００回合","别怂！！"]
    #print("test list train...")
    #test_chatter_list(list)
    print("test corpus train...")
    test_chatter_list(list)





