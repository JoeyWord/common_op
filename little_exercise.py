#!/usr/bin/env/py35
# coding=utf-8
import numpy as np

def circle_for_str(s):
    turn=0
    s_len=len(s)
    word_len_side=s_len//4 + 1
    circle_res = np.full((word_len_side,word_len_side),'')
    count = 0
    while(turn<4):
        for i in range(word_len_side):
            if turn==0:
                circle_res[turn,i] = s[count]
                count += 1
            elif turn==1 and i<word_len_side-1:
                circle_res[i+1,-1] = s[count]
                count += 1
            elif turn==2 and i>0:
                circle_res[-1,word_len_side-1-i] = s[count]
                count += 1
            elif turn==3 and i>0 and i<word_len_side-1:
                circle_res[word_len_side-1-i,0] = s[count]
                count += 1
            else:
                pass
            if count > s_len-1:
                break
        turn += 1
    return circle_res

