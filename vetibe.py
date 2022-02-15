#!/usr/bin/env/py35
# coding=utf-8
import numpy as np

def vertibeAlgth(obs,transform_prob,gen_prob,start_prob):
    """
    compute the most suitable route to construct the obs
    :param obs: generate the observation sequence
    :param transform_prob: the prob which is from i state to j state,i,j belong the number of states number format is array with two same dimension
    :param gen_prob: generate the obs prob.array with dim1 is same to state number and dim2 is same to obs value
    :param start_prob: origin state prob with length same to the length of states
    :return: list with best route
    """
    n_states = transform_prob.shape[0]
    n_obs = len(obs)

    obs_res = {}
    index = 0
    for x in obs:
        if x not in obs_res:
            obs_res[x] = index
            index += 1

    cache_prob_state = {}
    prob_0 = []
    state_start = [0 for _ in range(n_states)]
    best_route = [None]*n_obs
    for i in range(n_states):
        prob_0.append(gen_prob[i,obs_res[obs[0]]]*start_prob[i])
    cache_prob_state[0] = (prob_0,state_start)
    for t in range(1,n_obs-1):
        index_obs = obs_res[obs[t]]
        prob_t = [];prev_state_chooses = []
        for cur_state in range(n_states):
            prob_cur_t = []
            for prev_state in range(n_states):
                tmp = cache_prob_state[t - 1][0][cur_state] * transform_prob[prev_state, cur_state]
                prob_cur_t.append(tmp*gen_prob[cur_state,index_obs])
            prob_cur = max(prob_cur_t)
            prev_state_choose = np.argmax(prob_cur_t)
            prob_t.append(prob_cur)
            prev_state_chooses.append(prev_state_choose)
        cache_prob_state[t] = (prob_t,prev_state_chooses)
    prob_last = [];state_last = []
    obs_last = obs_res[obs[n_obs - 1]]
    for s in range(n_states):
        prob_last_s = max(cache_prob_state[n_obs-2][0][s]*transform_prob[:,s]*gen_prob[s,obs_last])
        state_last_s = np.argmax(cache_prob_state[n_obs-2][0][s]*transform_prob[:,s])
        prob_last.append(prob_last_s)
        state_last.append(state_last_s)
    cache_prob_state[n_obs-1] = (prob_last,state_last)
    p_start = max(prob_last)
    last_state = np.argmax(prob_last)
    best_route[n_obs-1] = last_state
    i = n_obs-1
    while(i >= 1):
        prev_state = cache_prob_state[i][1][last_state]
        #route = last_state
        best_route[i-1] = prev_state
        last_state = prev_state
        i -= 1
    return best_route

if __name__ == '__main__':
    obs = ['红','白','红']
    A = np.array([[0.5,0.2,0.3],[0.3,0.5,0.2],[0.2,0.3,0.5]])
    B = np.array([[0.5,0.5],[0.4,0.6],[0.7,0.3]])
    pi = [0.2,0.4,0.4]
    best_route = vertibeAlgth(obs,A,B,pi)
    print(best_route)
