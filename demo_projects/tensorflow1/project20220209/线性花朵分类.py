from 图片处理 import get_images_labels
import tensorflow.compat.v1 as tf
import os
import numpy as np
tf.compat.v1.disable_eager_execution()
images,labels = get_images_labels()
sep = int(len(images)*0.95)
train_x,train_y = images[:sep],labels[:sep]
test_x,test_y = images[sep:],labels[sep:]
print("训练集大小:{},测试集大小:{}".format(sep,len(images)-sep))
input_data = tf.placeholder("float", shape=[None, 320,320,3],name="inputtest")
input_label = tf.placeholder("float", shape=[None, 5])

def weight_variable(shape):
    initial = tf.truncated_normal(shape,stddev=0.01)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1,shape=shape)
    return tf.Variable(initial)

def conv2d(x,W):
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x,ksize=[1,4,4,1],
                          strides=[1,4,4,1],padding='SAME')


W_fc1 = weight_variable([320*320*3,2])
b_fc1 = bias_variable([2])
h_pool3_flat = tf.reshape(input_data, [-1,320*320*3])
h_fc1 = tf.nn.tanh(tf.matmul(h_pool3_flat, W_fc1) + b_fc1)

# keep_prob = tf.placeholder('float')#定义dropout比例
# h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)#全连接层1进行dropout处理
W_fc2 = weight_variable([2, 5])
b_fc2 = bias_variable([5])
predictions = tf.nn.softmax(tf.matmul(h_fc1, W_fc2) + b_fc2,name="outputtest")
cross_entropy = tf.reduce_mean(-tf.reduce_sum(input_label * tf.log(predictions),reduction_indices=1))#加负号才是正值,这个正值越小越接近真实情况
# train_step = tf.train.AdamOptimizer().minimize(cross_entropy)
optimizer = tf.train.RMSPropOptimizer(0.01).minimize(cross_entropy)
right_position = tf.equal(tf.argmax(predictions, axis=1), tf.argmax(input_label,axis=1))#返回一维张量,长度为batch大小。二者相等的位置为1，不等的位置为0
accuracy = tf.reduce_mean(tf.cast(right_position, tf.float32))#显然,平均值就是准确率

epochs = 5#总的数据轮次
batch_size = 2#batch_size和训练数据量共同决定了一轮经过多少次迭代
iterations = int(len(train_x)/batch_size)
print("===============开始训练===================")
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for epoch in range(epochs):
        for iteration in range(iterations):
            #优化
            start = iteration*batch_size
            end = (iteration+1)*batch_size
            sess.run(optimizer,feed_dict={input_data:train_x[start:end],input_label:train_y[start:end]})
            if iteration %  5 == 0:
                train_accuracy = accuracy.eval(
                    feed_dict={input_data: train_x[start:end],
                               input_label: train_y[start:end]})
                print("训练准确度:{}".format(train_accuracy))
                print("损失为:",cross_entropy.eval(feed_dict={input_data:train_x[start:end],input_label:train_y[start:end]}))

        print("==================================================================================")
        test_accuracy = accuracy.eval(feed_dict={input_data: test_x, input_label: test_y})
        print("测试准确度:{}".format(test_accuracy))
        print("==================================================================================")
    frozen_graph_def = tf.graph_util.convert_variables_to_constants(sess, sess.graph_def, ['outputtest'])
    with tf.gfile.FastGFile("./models/classification_test.pb", mode='wb') as f:
        f.write(frozen_graph_def.SerializeToString())
