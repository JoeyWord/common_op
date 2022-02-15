# coding=utf-8
import tensorflow as tf
import numpy as np
from random import random
import os

def simpleLayer(lr,epoch,layers={"layer1":3,"layer2":4},is_multiclassify=False,optimial_type=0):
    """
    """
    
    x_ = tf.placeholder(tf.float32,shape=[None,3],name='input_x')
    y_ = tf.placeholder(tf.int32,[None,1],name='input_y')
    global_step = tf.Variable(0,trainable=False,name='global_step')
    if is_multiclassify:
        y_ = tf.placeholder(tf.int32,[None,3],name='multi_inputY')
    w_dict = {};b_dict = {}
    #input_shape = tf.shape(x_)[1]
    #output_shape = tf.shape(y_)[1]
    input_shape = 3
    output_shape = 3
    for layer in layers:
        print("layer:",layer)
        w_dict[layer] = tf.Variable(tf.random_normal([input_shape,layers[layer]]),name=layer + '_w')
        b_dict[layer] = tf.Variable(tf.zeros(layers[layer]),name=layer + '_b')
        input_shape = layers[layer]
    hidden_out = hidden_layer(x_,w_dict,b_dict)
    w_o = tf.Variable(tf.random_normal([input_shape,output_shape]),name="output_w",trainable=False)
    b_o = tf.Variable(tf.zeros(output_shape),name="output_b")
    logits = tf.matmul(hidden_out,w_o) + b_o
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_,logits=logits))
   
    if optimial_type == 0:
        opt = tf.train.AdamOptimizer(lr)
        var_grand = opt.compute_gradients(loss)
        clip_gv = [[tf.clip_by_value(g,-2,2),v] for g,v in var_grand]
        train_op = tf.train.AdamOptimizer(lr).apply_gradients(clip_gv,global_step)
    else:
        
        learning_rate = tf.train.exponential_decay(lr,global_step,decay_steps=100,decay_rate=0.96,staircase=True)
        opt = tf.train.GradientDescentOptimizer(learning_rate)
        var_grand = opt.compute_gradients(loss)
        clip_gv = [[tf.clip_by_value(g,-2,2),v] for g,v in var_grand]  #defend the gradients eplosion
        train_op = tf.train.GradientDescentOptimizer(learning_rate).apply_gradients(clip_gv,global_step)




    out_put = tf.nn.softmax(logits)
    # define cross_entroy loss
    #loss = -tf.reduce_mean(tf.cast(y_,tf.float32)*tf.log(out_put)+(1-tf.cast(y_,tf.float32))*tf.log(1-out_put))
    # train step construct with Adam
    #train_op = tf.train.AdamOptimizer(lr).minimize(loss) 
    
    #train_data gen
    x,y = data_gen(10000,3)
    x_test,y_test = data_gen(100,3)
    x_valid,y_valid = data_gen(100,3)
    init = tf.global_variables_initializer()
    batch_size = 100
    data_size = x.shape[0]
    batch_len = data_size // batch_size + 1
    saver = tf.train.Saver()
    if not os.path.isdir('test_model'):
        os.mkdir('test_model')
    maxmum = 0.0
    with tf.Session() as sess:
        sess.run(init)
        for i in range(epoch):
            for step in range(batch_len):
                batch_start = step*batch_size
                batch_end = min(batch_start+batch_size,data_size)
                #batch_data_x = x[batch_start:batch_end]
                globalStep,loss_value,_ = sess.run([global_step,loss,train_op],feed_dict={x_:x[batch_start:batch_end],y_:y[batch_start:batch_end]})
                print("iteration{}: 损失函数值为: {}".format(i,loss_value))
            if i % 10 == 0:
                #print("the current iteration:{}  loss:{}".format(i,loss))
                #output each layer params update result every hundred step
                w_res,b_res = sess.run([w_dict,b_dict],feed_dict={x_:x[batch_start:batch_end],y_:y[batch_start:batch_end]})
                step_per_epoch = globalStep % batch_len
                for layer in w_res:
                    print("iteration {}: globalStep:{} and step_per_epoch/batch_len:{}/{} --- the {} :weight={} and bias={}".format(i,globalStep,step_per_epoch,batch_len,layer,w_res[layer],b_res[layer]))
            pred = sess.run(out_put,feed_dict={x_:x_valid})
            if is_multiclassify:
                f1_score = evaluate_multiclassify(pred,y_valid)
            else:
                f1_score = evaluate(pred,y_valid)

            if f1_score > maxmum:
                maxmum = f1_score
                saver.save(sess,os.path.join('test_model','model.ckpt'))
                test_pred = sess.run(out_put,feed_dict={x_:x_test})
                if is_multiclassify:

                    f1_score_test = evaluate_multiclassify(test_pred,y_test)
                else:
                    f1_score_test = evaluate(test_pred,y_test)
                print("the current iteration:{} f1_score_test:{}".format(i,f1_score_test))
        print("\n\nouput the terminal model test result:")
        print("now loading the model...")
        ckpt = tf.train.get_checkpoint_state('test_model')
        if ckpt and tf.train.checkpoint_exists(ckpt.model_checkpoint_path):
            print("loading params from trained model...")
            saver.restore(sess,ckpt.model_checkpoint_path)
            pred = sess.run(out_put,feed_dict={x_:x_test})
            f1_score = evaluate_multiclassify(pred,y_test)
            print("the terminal model save get the score result:",f1_score)

def hidden_layer(input_x,w,b):
    for layer in w:
        output = tf.nn.relu(tf.matmul(input_x,w[layer])+b[layer])
        input_x = output
    return output   
def evaluate_multiclassify(pred,real):
    tags_num = real.shape[-1]
    pred_tag = pred.argmax(axis=-1)
    real_tag = real.argmax(axis=-1)
    tp = np.array([0.0]*(tags_num+1))
    fp = np.array([0.0]*(tags_num+1))
    fn = np.array([0.0]*(tags_num+1))
    fb1 = np.array([0.0]*(tags_num+1))
    recall = np.array([0.0]*(tags_num+1))
    precision = np.array([0.0]*(tags_num+1))
    for i in range(len(real_tag)):
        if real_tag[i] == pred_tag[i]:
            tp[real_tag[i]] += 1
        else:
            fp[pred_tag[i]] += 1
            fn[real_tag[i]] += 1
    tp[tags_num] = sum(tp[:tags_num])
    fp[tags_num] = sum(fp[:tags_num])
    fn[tags_num] = sum(fn[:tags_num])
    accuracy = round(tp[tags_num]/len(real_tag),4)
    print("整个数据集的通过训练模型后的准确率:accuracy={}".format(accuracy))
    for i in range(len(fb1)):
        if max(tp[i],fp[i]) > 0:
            precision[i] = round(tp[i]/(tp[i]+fp[i]),4)

        if max(tp[i],fn[i]) > 0:

            recall[i] = round(tp[i]/(tp[i]+fn[i]),4)
        if max(precision[i],recall[i]) > 0:
            fb1[i] = round(200*precision[i]*recall[i]/(precision[i]+recall[i]),2)
        if i<len(fb1)-1:
            print("类{}的指标效果:precision={}%,recall={}%,fb_score={}".format(i,precision[i]*100,recall[i]*100,fb1[i]))
        else:
            print("最终的整体效果:precision={}%,recall={}%,fb_score={}".format(precision[i]*100,recall[i]*100,fb1[i]))
    
    return fb1[-1]
        

def evaluate(pred,real):
    fb1 = 0
    pred_onehot = [1 if x>=0.5 else 0 for x in pred]
    real = real.reshape([len(real),])
    tp = 0;cor = 0
    i = 0
    while i < len(real):
        if real[i] & pred_onehot[i]:
            tp += 1
        if (real[i] ^ pred_onehot[i])==0:
            cor += 1
        i += 1
    accuracy = round(cor/len(real),4)
    if sum(pred_onehot)>0 and sum(real)>0:
        precision = round(tp/sum(pred_onehot),4)
        recall = round(tp/sum(real),4)
        if precision>0 or recall>0:
            fb1 = 2*100*precision*recall/(precision+recall)
            print("valid info print:\naccuracy={}%;precision={}%;recall={}%;fb1={}".format(accuracy*100,precision*100,recall*100,fb1))
        else:
            print("precison and recall all equal 0")
    else:
        print("invalid info to perform but the accuracy={}".format(accuracy))

    return fb1
def data_gen(data_size,feature_nums,num_tags=3):
    x = np.random.random((data_size,feature_nums))
    y = np.zeros((data_size,num_tags))
    for idx,feat in enumerate(x):
        if feat[0]**2 + feat[1]**2 + feat[2]**2 < 1:
            y[idx][0] = 1
        elif feat[0]**2 + feat[1]**2 + feat[2]**2>=1 and feat[0]**2 + feat[1]**2 + feat[2]**2<2:
            y[idx][1] = 1
        else:
            y[idx][2] = 1
    return x,y

            
if __name__ == '__main__':
    simpleLayer(lr=0.002,epoch=100,is_multiclassify=True,optimial_type=0)



            


    

    