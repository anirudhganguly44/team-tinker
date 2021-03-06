import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from network.DenseNet.utils import *
from tensorpack import *
from tensorpack.models.batch_norm import *
weight_decay = 0.0005

class DenseNet(object):
    def __init__(self, depth, growthRate, image_shape, num_labels, scope='DenseNet'):
        
        self.N = int((depth-4)/3)
        self.growthRate = growthRate
        self.image_shape = image_shape
        self.num_labels = num_labels
        self.scope = scope

        [height, width, channels] = image_shape
        train_batch_shape = [None, height, width, channels]

        with tf.compat.v1.variable_scope(self.scope):
            self.train_image_placeholder = tf.compat.v1.placeholder(
                tf.float32,
                shape=train_batch_shape,
                name= 'train_images'
            )
            self.train_label_placeholder = tf.compat.v1.placeholder(
                tf.int32,
                shape=[None, ],
                name= 'train_labels'
            )
            test_batch_shape = [None, height, width, channels]
            self.test_image_placeholder = tf.compat.v1.placeholder(
                tf.float32,
                shape=test_batch_shape,
                name= 'test_images'
            )
            self.test_label_placeholder = tf.compat.v1.placeholder(
                tf.int32,
                shape=[None, ],
                name= 'test_labels'
            )

    def build_network(self, images, is_training, reuse):
        if is_training:
            with TowerContext("", is_training=True):
                with tf.compat.v1.variable_scope(self.scope, reuse=reuse):
                    logits = self.inference(images)
        else:
            with TowerContext("", is_training=False):
                with tf.compat.v1.variable_scope(self.scope, reuse=reuse):
                    logits = self.inference(images)

        return tf.nn.softmax(logits), logits

    def inference(self, images):
        l = conv('conv0', images, 16, 1)
        with tf.compat.v1.variable_scope('block1') as scope:
            for i in range(self.N):
                l = add_layer('dense_layer.{}'.format(i), l, self.growthRate)
            l = add_transition('transition1', l)

        with tf.compat.v1.variable_scope('block2') as scope:
            for i in range(self.N):
                l = add_layer('dense_layer.{}'.format(i), l, self.growthRate)
            l = add_transition('transition2', l)

        with tf.compat.v1.variable_scope('block3') as scope:
            for i in range(self.N):
                l = add_layer('dense_layer.{}'.format(i), l, self.growthRate)

        l = BatchNorm('bnlast', l)
        l = tf.nn.relu(l)
        l = GlobalAvgPooling('gap', l)
        logits = FullyConnected('linear', l, out_dim=self.num_labels, nl=tf.identity)

        return logits

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
        
        l2_loss = tf.add_n([tf.nn.l2_loss(var) for var in tf.compat.v1.trainable_variables()])

        self.train_loss = tf.reduce_mean(loss) + l2_loss*weight_decay
        self.train_accuracy = tf.reduce_mean(tf.cast(prediction, tf.float32))
        self.learning_rate = tf.compat.v1.train.piecewise_constant(train_step, lr_boundaries, lr_values)

        if optimizer_type == "momentum":
            optimizer = tf.compat.v1.train.MomentumOptimizer(self.learning_rate, 0.9, use_nesterov=True)
        elif optimizer_type == "sgd":
            optimizer = tf.train.GradientDescentOptimizer(self.learning_rate)

        train_vars = [x for x in tf.compat.v1.trainable_variables() if self.scope in x.name]

        update_ops = tf.compat.v1.get_collection(tf.compat.v1.GraphKeys.UPDATE_OPS)
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

        return  self.test_loss, self.test_accuracy, loss, prob

