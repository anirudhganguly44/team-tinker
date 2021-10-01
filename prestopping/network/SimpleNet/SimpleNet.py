import sys, os
import tensorflow as tf
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from network.SimpleNet.utils import *

weight_decay = 0.0005

class SimpleNet(object):
    def __init__(self, image_shape, num_labels, scope='SimpleNet'):

        self.image_shape = image_shape
        self.num_labels = num_labels
        self.scope = scope

        [height, width, channels] = image_shape
        train_batch_shape = [None, height, width, channels]

        with tf.variable_scope(self.scope):
            self.train_image_placeholder = tf.placeholder(
                tf.float32,
                shape=train_batch_shape,
                name='train_images'
            )
            self.train_label_placeholder = tf.placeholder(
                tf.int32,
                shape=[None, ],
                name='train_labels'
            )
            test_batch_shape = [None, height, width, channels]
            self.test_image_placeholder = tf.placeholder(
                tf.float32,
                shape=test_batch_shape,
                name='test_images'
            )
            self.test_label_placeholder = tf.placeholder(
                tf.int32,
                shape=[None, ],
                name='test_labels'
            )

    def build_network(self, images, is_training, reuse):

        with tf.variable_scope(self.scope, reuse=reuse):

            batch_size = images.get_shape().as_list()[0]
            if is_training:
                keep_prob = 0.5
            else:
                keep_prob = 1.0

            #########################

            conv_1 = conv('conv_1', images, 64)
            conv_1 = batch_norm('conv_1_bn', conv_1, is_training, reuse)
            conv_1 = lrelu(conv_1)

            conv_2 = conv('conv_2', conv_1, 64)
            conv_2 = batch_norm('conv_2_bn', conv_2, is_training, reuse)
            conv_2 = lrelu(conv_2)
            conv_2 = tf.nn.max_pool(conv_2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

            conv_3 = conv('conv_3', conv_2, 128)
            conv_3 = batch_norm('conv_3_bn', conv_3, is_training, reuse)
            conv_3 = lrelu(conv_3)

            conv_4 = conv('conv_4', conv_3, 128)
            conv_4 = batch_norm('conv_4_bn', conv_4, is_training, reuse)
            conv_4 = lrelu(conv_4)
            conv_4 = tf.nn.max_pool(conv_4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")

            conv_5 = conv('conv_5', conv_4, 196)
            conv_5 = batch_norm('conv_5_bn', conv_5, is_training, reuse)
            conv_5 = lrelu(conv_5)

            conv_6 = conv('conv_6', conv_5, 196)
            conv_6 = batch_norm('conv_6_bn', conv_6, is_training, reuse)
            conv_6 = lrelu(conv_6)
            conv_6 = tf.nn.max_pool(conv_6, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
            #########################

            fc_7 = fully_connected('fc_7', conv_6, 256)
            fc_7 = batch_norm('fc_17_bn', fc_7, is_training, reuse)
            fc_7 = lrelu(fc_7)
            fc_7 = tf.nn.dropout(fc_7, keep_prob)

            fc_8 = fully_connected('output', fc_7, self.num_labels)

            return tf.nn.softmax(fc_8), fc_8



    def build_train_op(self, lr_boundaries, lr_values, optimizer_type):
        train_step = tf.Variable(initial_value=0, trainable=False, name="train_step")

        self.train_step = train_step

        prob, logits = self.build_network(self.train_image_placeholder, True, False)
        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=self.train_label_placeholder,
            logits=logits
        )

        prediction = tf.equal(tf.cast(tf.argmax(prob, axis=1), tf.int32), self.train_label_placeholder)
        prediction = tf.cast(prediction, tf.float32)

        l2_loss = tf.add_n([tf.nn.l2_loss(var) for var in tf.trainable_variables()])

        self.train_loss = tf.reduce_mean(loss) + l2_loss * weight_decay
        self.train_accuracy = tf.reduce_mean(tf.cast(prediction, tf.float32))
        self.learning_rate = tf.train.piecewise_constant(train_step, lr_boundaries, lr_values)

        if optimizer_type == "momentum":
            optimizer = tf.train.MomentumOptimizer(self.learning_rate, 0.9, use_nesterov=True)
        elif optimizer_type == "sgd":
            optimizer = tf.train.GradientDescentOptimizer(self.learning_rate)
        elif optimizer_type == "adam":
            optimizer = tf.train.AdamOptimizer(self.learning_rate)

        train_vars = [x for x in tf.trainable_variables() if self.scope in x.name]

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            train_op = optimizer.minimize(self.train_loss, global_step=train_step, var_list=train_vars)

        return self.train_loss, self.train_accuracy, train_op, loss, prob

    def build_test_op(self):
        prob, logits = self.build_network(self.test_image_placeholder, False, True)

        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=self.test_label_placeholder,
            logits=logits
        )

        prediction = tf.equal(tf.cast(tf.argmax(prob, axis=1), tf.int32), self.test_label_placeholder)
        prediction = tf.cast(prediction, tf.float32)

        self.test_loss = tf.reduce_mean(loss)
        self.test_accuracy = tf.reduce_mean(prediction)

        return self.test_loss, self.test_accuracy, loss, prob

