import time, sys
import tensorflow as tf
from termcolor import colored
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from structure.trainer import *

class Default(object):

    def __init__(self, reader, configuration):
        self.reader = reader
        self.configuration = configuration

    def train(self):

        if self.reader == None or self.configuration == None:
            print(colored("[ERROR]", "red"), "Please call data_preparation function first")
            sys.exit(1)

        training_log = []

        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.visible_device_list = str(self.configuration.gpu_id)
        config.gpu_options.allow_growth = True
        graph = tf.Graph()

        with graph.as_default():
            with tf.device('/gpu:' + str(self.configuration.gpu_id)):
                with tf.Session(config=config) as sess:

                    if self.configuration.model_name not in ["DenseNet-10-12", "DenseNet-25-12", "DenseNet-40-12", "VGG-19"]:
                        print(colored("[ERROR]", "red"), "model name", self.configuration.model_name)
                        print(colored("[ERROR]", "red"), "Model name must be defined in [DenseNet-10-12", "DenseNet-25-12", "DenseNet-40-12", "VGG-19]")
                        sys.exit(1)

                    if self.configuration.model_name == "DenseNet-40-12":
                        model = DenseNet(40, 12, self.reader.get_input_shape(), self.reader.get_num_labels())
                    elif self.configuration.model_name == "DenseNet-25-12":
                        model = DenseNet(25, 12, self.reader.get_input_shape(), self.reader.get_num_labels())
                    elif self.configuration.model_name == "DenseNet-10-12":
                        model = DenseNet(10, 12, self.reader.get_input_shape(), self.reader.get_num_labels())
                    elif self.configuration.model_name == "VGG-19":
                        model = VGG19(self.reader.get_input_shape(), self.reader.get_num_labels())

                    # register training operations on Trainer class
                    trainer = Trainer(model)
                    trainer.train_loss_op, trainer.train_accuracy_op, trainer.train_op, trainer.train_xentropy_op, trainer.train_prob_op = \
                        model.build_train_op(self.configuration.lr_boundaries, self.configuration.lr_values, self.configuration.optimizer)
                    trainer.test_loss_op, trainer.test_accuracy_op, trainer.test_xentropy_op, trainer.test_prob_op = model.build_test_op()
                    trainer.init_op = tf.global_variables_initializer()

                    ######################## main part for pre-training #######################
                    start = time.time()
                    sess.run(trainer.init_op)
                    print(colored("[LOG]", "blue"), colored(("[Pre-training procedure] starts " + str(self.configuration.total_epoch) + " epochs"), "green"))
                    self.training(sess, trainer, training_log)
                    print(colored("[TIME]", "magenta"), str(round(time.time() - start, 2)) + " seconds took for Phase II")
                    #########################################################################################

                    sess.close()

        f = open(self.configuration.log_path + "/convergence_log.csv", "w")

        for text in training_log:
            f.write(text + "\n")
        f.close()

    def training(self, sess, trainer, training_log):

        for epoch in range(self.configuration.total_epoch):
            avg_train_loss = 0.0
            avg_train_acc = 0.0

            # Train
            for i in range(self.reader.train_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.train_patcher.get_next_random_mini_batch()
                train_loss, train_acc, _ = sess.run([trainer.train_loss_op, trainer.train_accuracy_op, trainer.train_op], feed_dict={trainer.model.train_image_placeholder: images, trainer.model.train_label_placeholder: labels})
                avg_train_loss += train_loss
                avg_train_acc += train_acc

            avg_train_loss /= self.reader.train_patcher.num_iters_per_epoch
            avg_train_acc /= self.reader.train_patcher.num_iters_per_epoch

            # Validation
            avg_val_loss = 0.0
            avg_val_acc = 0.0
            for i in range(self.reader.validation_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.validation_patcher.get_eval_mini_batch(i)
                val_loss, val_acc = sess.run([trainer.test_loss_op, trainer.test_accuracy_op], feed_dict={trainer.model.test_image_placeholder: images, trainer.model.test_label_placeholder: labels})
                avg_val_loss += val_loss
                avg_val_acc += val_acc
            avg_val_loss /= self.reader.validation_patcher.num_iters_per_epoch
            avg_val_acc /= self.reader.validation_patcher.num_iters_per_epoch

            # Test
            avg_test_loss = 0.0
            avg_test_acc = 0.0
            for i in range(self.reader.test_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.test_patcher.get_eval_mini_batch(i)
                val_loss, val_acc = sess.run([trainer.test_loss_op, trainer.test_accuracy_op], feed_dict={trainer.model.test_image_placeholder: images, trainer.model.test_label_placeholder: labels})
                avg_test_loss += val_loss
                avg_test_acc += val_acc
            avg_test_loss /= self.reader.test_patcher.num_iters_per_epoch
            avg_test_acc /= self.reader.test_patcher.num_iters_per_epoch

            # training log
            cur_lr = sess.run(trainer.model.learning_rate)
            print((epoch + 1), ", ", cur_lr, ", ", avg_train_loss,  ", ", 1.0-avg_train_acc, ", ", avg_val_loss, ", ", 1.0-avg_val_acc, ", ", avg_test_loss, ", ", 1.0-avg_test_acc)
            if training_log is not None:
                training_log.append(str(epoch + 1) + ", " + str(cur_lr) + ", " + str(avg_train_loss) + ", " + str(1.0 - avg_train_acc) + ", " + str(avg_val_loss) + ", " + str(1.0 - avg_val_acc) + ", " + str(avg_test_loss) + ", " + str(1.0 - avg_test_acc))
