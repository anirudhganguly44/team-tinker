import time, sys
import tensorflow as tf
from termcolor import colored
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from structure.trainer import *
from correcter.collaboration_correcter import *

class Phase_III(object):

    def __init__(self, reader, configuration, queue_size=15, threshold=0.05, restart=3):
        self.reader = reader
        self.configuration = configuration
        self.queue_size = queue_size
        self.threshold = threshold
        self.restart = restart
        self.min_val_error = 1.0

    def train_by_selfie(self):

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

                    ######################## main part for pre-training ####################################
                    start = time.time()
                    sess.run(trainer.init_op)
                    self.correcter = Correcter(self.reader, queue_size=self.queue_size, threshold=self.threshold)
                    for i in range(self.restart + 1):

                        print(colored("[LOG]", "blue"), "Run: ", (i + 1), "(Restart " + str(i) + "/" + str(self.restart) + ")")
                        sess.run(trainer.init_op)
                        print(colored("[LOG]", "blue"), colored(("[Pre-training procedure] starts " + str(self.configuration.total_epoch) + " epochs"), "green"))
                        self.training(sess, trainer, training_log)
                        print(colored("[TIME]", "magenta"), (i + 1), "(Restart " + str(i) + ")", str(round(time.time() - start, 2)) + " seconds took for training")
                        self.correcter.predictions_clear()
                        self.report_changed_noise_rate()
                    ########################################################################################
                    sess.close()

        self.correcter.save_images_orig("cleandataset")
        f = open(self.configuration.collaboration_path + "/phase_III_convergence_log.csv", "w")
        for text in training_log:
            f.write(text + "\n")
        f.close()

    def training(self, sess, trainer, training_log):

        for epoch in range(self.configuration.total_epoch):
            avg_train_loss = 0.0
            avg_train_acc = 0.0
            avg_clean_hit_ratio = 0.0
            avg_correction_hit_ratio = 0.0
            avg_clean_sample = 0.0
            avg_corrected_sample = 0.0

            if epoch < self.configuration.warm_up_epoch:
                for i in range(self.reader.train_patcher.num_iters_per_epoch):
                    ids, images, labels = self.reader.train_patcher.get_next_random_mini_batch()
                    train_loss, train_acc, train_softmax, _ = sess.run([trainer.train_loss_op, trainer.train_accuracy_op, trainer.train_prob_op, trainer.train_op], feed_dict={trainer.model.train_image_placeholder: images, trainer.model.train_label_placeholder: labels})
                    self.correcter.async_update_prediction_matrix(ids, train_softmax)

                    avg_train_loss += train_loss
                    avg_train_acc += train_acc

            else:
                for i in range(self.reader.train_patcher.num_iters_per_epoch):
                    ids, images, labels = self.reader.train_patcher.get_next_random_mini_batch()

                    # inference for loss
                    train_softmax = sess.run(trainer.train_prob_op, feed_dict={trainer.model.train_image_placeholder: images, trainer.model.train_label_placeholder: labels})
                    self.correcter.async_update_prediction_matrix(ids, train_softmax)

                    # select maximal safe set and refurbishable samples
                    selected_ids, selected_images, selected_labels, num_clean, num_corrected, clean_hit, correction_hit = self.correcter.patch_clean_with_corrected_sample_batch(ids, images, labels)

                    # backward prop on them
                    _ = sess.run(trainer.train_op, feed_dict={trainer.model.train_image_placeholder: selected_images, trainer.model.train_label_placeholder: selected_labels})

                    # for log
                    new_labels_for_log = []
                    for j in range(len(ids)):
                        if self.correcter.corrected_labels[ids[j]] == -1:
                            new_labels_for_log.append(labels[j])
                        else:
                            new_labels_for_log.append(self.correcter.corrected_labels[ids[j]])

                    train_loss, train_acc = sess.run([trainer.train_loss_op, trainer.train_accuracy_op], feed_dict={trainer.model.train_image_placeholder: images, trainer.model.train_label_placeholder: new_labels_for_log})

                    avg_train_loss += train_loss
                    avg_train_acc += train_acc
                    avg_clean_hit_ratio += clean_hit
                    avg_correction_hit_ratio += correction_hit
                    avg_clean_sample += num_clean
                    avg_corrected_sample += num_corrected

                avg_clean_hit_ratio /= self.reader.train_patcher.num_iters_per_epoch
                avg_correction_hit_ratio /= self.reader.train_patcher.num_iters_per_epoch
                avg_clean_sample /= self.reader.train_patcher.num_iters_per_epoch
                avg_corrected_sample /= self.reader.train_patcher.num_iters_per_epoch

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
            print((epoch + 1), ", ", cur_lr, ", ", avg_train_loss, ", ", 1.0 - avg_train_acc, ", ", avg_val_loss, ", ", 1.0 - avg_val_acc, ", ", avg_test_loss, ", ", 1.0 - avg_test_acc, ", ", avg_clean_sample, ", ", avg_clean_hit_ratio, ", ", avg_corrected_sample, ", ", avg_correction_hit_ratio)
            if training_log is not None:
                training_log.append(str(epoch + 1) + ", " + str(cur_lr) + ", " + str(avg_train_loss) + ", " + str(1.0 - avg_train_acc) + ", " + str(avg_val_loss) + ", " + str(1.0 - avg_val_acc) + ", " + str(avg_test_loss) + ", " + str(1.0 - avg_test_acc) + ", " + str(avg_clean_sample) + ", " + str(avg_clean_hit_ratio) + ", " + str(avg_corrected_sample) + ", " + str(avg_correction_hit_ratio))


    def report_changed_noise_rate(self):

        # report noise rate of corrected data
        corrected_noise_rate = 1.0

        for id in range(len(self.reader.train_data)):
            if self.correcter.corrected_labels[id] == -1:
                noisy_label = self.reader.train_data[id].label
            else:
                noisy_label = self.correcter.corrected_labels[id]

            if noisy_label == self.reader.train_data[id].true_label:
                corrected_noise_rate += 1.0

        given_noise_rate = self.reader.noise_rate
        corrected_noise_rate /= float(len(self.reader.train_data))
        corrected_noise_rate = 1.0 - corrected_noise_rate

        f = open(self.configuration.pretrain_path + "/changed_noise_rate.csv", "w")
        f.write("Given noise rate, " + str(given_noise_rate) + ", Modified noise rate, " + str(corrected_noise_rate))
        f.close()