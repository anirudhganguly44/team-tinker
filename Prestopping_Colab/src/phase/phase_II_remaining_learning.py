import os, time, sys
import tensorflow as tf
from termcolor import colored
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from structure.history import *
from structure.trainer import *

import numpy as np


class Phase_II(object):

    def __init__(self, reader, configuration, load_path=None):
        self.reader = reader
        self.configuration = configuration
        self.load_path = load_path

        if self.load_path is None:
            print(colored("[ERROR]", "red"), "There is no pretrained model to load from", self.load_path)
            sys.exit(1)

    def stable_training(self):

        if self.reader == None or self.configuration == None:
            print(colored("[ERROR]", "red"), "Please call data_preparation function first")
            sys.exit(1)

        training_log = []

        config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
        config.gpu_options.visible_device_list = str(self.configuration.gpu_id)
        config.gpu_options.allow_growth = True
        graph = tf.Graph()

        with graph.as_default():
            with tf.device('/gpu:' + str(self.configuration.gpu_id)):
                with tf.compat.v1.Session(config=config) as sess:

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
                    trainer.init_op = tf.compat.v1.global_variables_initializer()

                    ######################## main part for extracting trusted samples #######################
                    start = time.time()
                    saver = tf.compat.v1.train.Saver()
                    history = History(self.reader, self.configuration.queue_size)

                    # restore
                    print(colored("[LOG]", "blue"), "Loads pre-trained model from", self.load_path)
                    saver.restore(sess, self.load_path + "/saved/model.ckpt")
                    history.restore(self.load_path + "/history_backup")

                    train_vars = [x for x in tf.compat.v1.global_variables() if 'train_step' in x.name]
                    cur_iterations = sess.run(train_vars[0])
                    total_iterations = self.reader.train_patcher.num_iters_per_epoch * self.configuration.total_epoch
                    self.remaining_epoch = int(np.ceil(float(total_iterations - cur_iterations) / float(self.reader.train_patcher.num_iters_per_epoch)))
                    self.stopped_epoch = self.configuration.total_epoch - self.remaining_epoch
                    print(colored("[LOG]", "blue"), "Pretrained model was stopped at", self.stopped_epoch, "out of", self.configuration.total_epoch, "epochs")
                    print(colored("[LOG]", "blue"), "The stable learning process will be executed during the remaining schedule of", self.remaining_epoch, "out of", self.configuration.total_epoch, "epochs")
                    print(colored("[LOG]", "blue"), colored(("[Stable learning procedure] starts " + str(self.remaining_epoch) + " epochs"), "green"))

                    # extracting
                    self.training(sess, trainer, history, training_log)
                    print(colored("[TIME]", "magenta"), str(round(time.time() - start, 2)) + " seconds took for Phase I")
                    #########################################################################################

                    sess.close()

        f = open(self.configuration.extracting_path + "/phase_II_convergence_log.csv", "w")
        for text in training_log:
            f.write(text + "\n")
        f.close()

        self.configuration.trusted_meta_path = self.save_extracting_sample_meta(history)

    def training(self, sess, trainer, history, training_log):

        for epoch in range(self.remaining_epoch):
            avg_train_loss = 0.0
            avg_train_acc = 0.0
            avg_hit_ratio = 0.0
            avg_clean_sample = 0.0

            for i in range(self.reader.train_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.train_patcher.get_next_random_mini_batch()

                # inference for log
                train_loss, train_acc, train_softmax = sess.run([trainer.train_loss_op, trainer.train_accuracy_op, trainer.train_prob_op], feed_dict={trainer.model.train_image_placeholder: images, trainer.model.train_label_placeholder: labels})
                history.async_update_prediction_matrix(ids, train_softmax)

                # get trusted samples
                trusted_ids, trusted_images, trusted_labels, hit_ratio = history.get_trusted_samples(self.reader, ids, images, labels)

                # backward prop on squeezed clean samples
                _ = sess.run(trainer.train_op, feed_dict={trainer.model.train_image_placeholder: trusted_images, trainer.model.train_label_placeholder: trusted_labels})

                avg_train_loss += train_loss
                avg_train_acc += train_acc
                avg_hit_ratio += hit_ratio
                avg_clean_sample += len(trusted_ids)

            avg_hit_ratio /= self.reader.train_patcher.num_iters_per_epoch
            avg_clean_sample /= self.reader.train_patcher.num_iters_per_epoch

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

            full_decisions = history.compute_decision_for_dataset()
            num_fitted_unclean = 0
            num_fitted_clean = 0

            for id in range(len(full_decisions)):
                if full_decisions[id]:
                    if self.reader.train_data[id].label == self.reader.train_data[id].true_label:
                        num_fitted_clean += 1
                    else:
                        num_fitted_unclean += 1

            # training log
            cur_lr = sess.run(trainer.model.learning_rate)
            print((self.stopped_epoch+ epoch + 1), ", ", cur_lr, ", ", avg_train_loss,  ", ", 1.0-avg_train_acc, ", ", avg_val_loss, ", ", 1.0-avg_val_acc, ", ", avg_test_loss, ", ", 1.0-avg_test_acc, ", ", avg_clean_sample, ", ", avg_hit_ratio, ", ", num_fitted_clean, ", ", num_fitted_unclean)
            if training_log is not None:
                training_log.append(str(self.stopped_epoch + epoch + 1) + ", " + str(cur_lr) + ", " + str(avg_train_loss) + ", " + str(1.0 - avg_train_acc) + ", " + str(avg_val_loss) + ", " + str(1.0 - avg_val_acc) + ", " + str(avg_test_loss) + ", " + str(1.0 - avg_test_acc) + ", " + str(avg_clean_sample) + ", " + str(avg_hit_ratio) + ", " + str(num_fitted_clean) + ", " + str(num_fitted_unclean))

    def save_extracting_sample_meta(self, history):
        decisions = history.compute_decision_for_dataset()

        f = open(self.configuration.extracting_path + "/trusted_samples.csv", "w")

        # sample type: [0: selected, 1: not selected]
        for i in range(len(decisions)):
            if decisions[i]:
                f.write(str(i) +  ", " + str(self.reader.train_data[i].label) + ", 0\n")
            else:
                f.write(str(i) +  ", " + str(self.reader.train_data[i].label) + ", 1\n")
        f.close()

        history.save_history(self.configuration.extracting_path + "/history_backup")

        print(colored("[LOG]", "blue"), "Finish to write the summary of extracted trusted samples")

        return os.getcwd() + "/" + f.name


