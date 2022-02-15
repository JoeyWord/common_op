#!/usr/bin/env/py35
# coding=utf-8
import tensorflow as tf
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from tensorflow.contrib.layers.python.layers.layers import fully_connected

from utils import get_log



def gen_data(seq,time_step,seq_length):
    x=[];y=[]
    for i in range(seq_length-time_step):
        x.append(seq[i:i+time_step])
        y.append(seq[i+time_step])
    return np.array(x,dtype=np.float32),np.array(y,dtype=np.float32)
def fully_connect(inputs,full_size,tags):
    input_shape = tf.shape(inputs)[-1]
    with tf.variable_scope("full_connect1"):
        weight_fc1 = tf.get_variable("weight_fc1",shape=[input_shape,full_size],dtype=tf.float32,initializer=tf.truncated_normal_initializer())
        bias_fc1 = tf.get_variable("bias_fc1",shape=[full_size],dtype=tf.float32,initializer=tf.constant_initializer())
        fc1_output = tf.nn.relu(tf.matmul(inputs,weight_fc1) + bias_fc1)
    with tf.variable_scope("full_connect2"):
        weight_fc2 = tf.get_variable("weight_fc2",shape=[full_size,tags],dtype=tf.float32,initializer=tf.truncated_normal_initializer())
        bias_fc2 = tf.get_variable("bias_fc2",shape=[tags],dtype=tf.float32,initializer=tf.constant_initializer())
        fc2_output = tf.matmul(fc1_output,weight_fc2) + bias_fc2
    return fc2_output

def gen_config(*args):
    config = {}
    config["hs"] = args[0]
    config["nl"] = args[1]
    config["ts"] = args[2]
    config["en"] = args[3]
    config["tn"] = args[4]
    config["ts"] = args[5]
    config["epoch"] = args[6]
    return config

class RNNmodel():
    def __init__(self,config,logger):
        self.hidden_size = config["hs"]
        self.num_layers = config["nl"]
        self.time_step = config["ts"]
        self.example_nums = config["en"]
        self.test_nums = config["tn"]
        self.test_start = config["ts"]
        self.epoch = config["epoch"]
        self.logger = logger

    def model(self,input_X,input_Y,is_train=True):
        lstm_base = tf.nn.rnn_cell.BasicLSTMCell(self.hidden_size)
        cells = tf.nn.rnn_cell.MultiRNNCell([lstm_base for _ in self.num_layers])
        if is_train:
            cells = tf.nn.rnn_cell.MultiRNNCell([tf.nn.rnn_cell.DropoutWrapper(lstm_base,input_keep_prob=self.keep_prob) for _ in range(self.num_layers)])

        outputs,output_state = tf.nn.dynamic_rnn(cells,input_X,sequence_length=self.time_step)
        #compute mean square error
        preds = fully_connected(outputs[:,-1,:])
        if not is_train:
            return preds,None,None
        with tf.variable_scope("loss",reuse=None):
            loss = tf.losses.mean_squared_error(preds,input_Y)
            learning_rate = tf.train.exponential_decay(self.learning_rate,global_step=self.global_step,decay_steps=self.decay_steps,decay_rate=self.decay_rate)
            train_op = tf.train.GradientDescentOptimizer(learning_rate).minimize(tf.losses.get_total_loss)
        return preds,loss,train_op

    def train(self,sess,train_x,train_y):
        sess.run(self.iniitailizer)
        self.preds,self.loss,self.train_op = self.model(train_x,train_y)
        for step in range(self.epoch):
            prediction,loss,train_op = sess.run([self.preds,self.loss,self.train_op])
            if (step+1) % 10 == 0 or step==self.epoch-1:
                self.logger.info("iteration: %d and loss value is: %9.6f" %(step,loss))
        return sess

    def run_eval(self,sess,test_x,test_y):
        sess.run(self.initializer)

        predicions,_,_ = self.model(test_x,test_y,is_train=False)
        pred = sess.run(predicions)
        mse = np.sqrt(((np.array(pred)-test_y)**2).mean(axis=-1))
        self.logger.info("test data generate mse value:%5.2f" %mse)
        #x_range = range(test_x.shape[0])
        fig = plt.figure()
        plt.plot(pred,'--o',label='pred_value')
        plt.plot(test_y,'**k',label='real_value')
        plt.legend()
        plt.show()

if __name__ == '__main__':
    config_info = (1024,2,10,1000,100,500,20)
    config = gen_config(*config_info)
    logger = get_log('log/rnn_test.log')
    rnn_model = RNNmodel(config,logger)
    seq = np.sin(np.linspace(0,1000,rnn_model.example_nums))
    train_x,train_y = gen_data(seq)
    test_seq = np.sin(np.linspace(rnn_model.test_start,rnn_model.test_start + rnn_model.test_nums,num=rnn_model.test_nums))
    test_x,test_y = gen_data(test_seq)
    with tf.Session() as sess:
        sess = rnn_model.train(sess,train_x,train_y)
        rnn_model.run_eval(sess,test_x,test_y)

