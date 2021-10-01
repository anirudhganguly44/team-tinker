import tensorflow as tf
import numpy as np
from tensorpack import *

def conv(name, input_layer, output_dim, use_bias = True):
    return Conv2D(name, input_layer, output_dim, 3, stride=1, nl=tf.identity, use_bias=use_bias, W_init=tf.random_normal_initializer(stddev=np.sqrt(2.0 / 9 / output_dim)))

def fully_connected(scope, layer, out_dim):
    return FullyConnected(scope, layer, out_dim=out_dim, nl=tf.identity)

def batch_norm(scope, input_layer, is_training, reuse):
    output_layer = tf.contrib.layers.batch_norm(
        input_layer,
        decay=0.9,
        scale=True,
        epsilon=1e-5,
        is_training=is_training,
        reuse=reuse,
        scope=scope
    )

    return output_layer


def lrelu(input_layer):
    output_layer = tf.nn.relu(input_layer)
    return output_layer


def avg_pool(scope, input_layer, ksize=None, strides=[1, 2, 2, 1]):
    if ksize is None:
        ksize = strides

    with tf.variable_scope(scope):
        output_layer = tf.nn.avg_pool(input_layer, ksize, strides, 'VALID')
        return output_layer


def Global_Average_Pooling(x, stride=1):
    width = np.shape(x)[1]
    height = np.shape(x)[2]
    pool_size = [width, height]
    return tf.layers.average_pooling2d(inputs=x, pool_size=pool_size, strides=stride)