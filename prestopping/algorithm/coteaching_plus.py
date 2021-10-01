import time, sys, operator
import tensorflow as tf
import numpy as np
from termcolor import colored
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from network.SimpleNet.SimpleNet import *
from structure.trainer import *

class CoteachingPlus(object):

    def __init__(self, reader, configuration):
        self.reader = reader
        self.configuration = configuration
    def train(self):

        if self.reader == None or self.configuration == None:
            print(colored("[ERROR]", "red"), "Please call data_preparation function first")
            sys.exit(1)

        # gpu setup
        if type(self.configuration.gpu_id) is int:
            gpu_ids = str(self.configuration.gpu_id)
        elif type(self.configuration.gpu_id) is str:
            gpu_ids = self.configuration.gpu_id
        else:
            sys.exit(1)

        # training log
        training_log = []

        # tf conf
        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.visible_device_list = gpu_ids
        config.gpu_options.allow_growth = True
        graph = tf.Graph()

        with graph.as_default():
            with tf.Session(config=config) as sess:

                if self.configuration.model_name not in ["DenseNet-10-12", "DenseNet-25-12", "DenseNet-40-12", "VGG-19", "SimpleNet"]:
                    print(colored("[ERROR]", "red"), "model name", self.configuration.model_name)
                    print(colored("[ERROR]", "red"), "Model name must be defined in [DenseNet-10-12, DenseNet-25-12, DenseNet-40-12, VGG-19, SimpleNet]")
                    sys.exit(1)

                models = []

                for model_num in range(2):
                    if self.configuration.model_name == "DenseNet-40-12":
                        model = DenseNet(40, 12, self.reader.get_input_shape(), self.reader.get_num_labels(), scope=("network" + str(model_num)))
                    elif self.configuration.model_name == "DenseNet-25-12":
                        model = DenseNet(25, 12, self.reader.get_input_shape(), self.reader.get_num_labels(), scope=("network" + str(model_num)))
                    elif self.configuration.model_name == "DenseNet-10-12":
                        model = DenseNet(10, 12, self.reader.get_input_shape(), self.reader.get_num_labels(), scope=("network" + str(model_num)))
                    elif self.configuration.model_name == "VGG-19":
                        model = VGG19(self.reader.get_input_shape(), self.reader.get_num_labels(), scope=("network" + str(model_num)))
                    elif self.configuration.model_name == "SimpleNet":
                        model = SimpleNet(self.reader.get_input_shape(), self.reader.get_num_labels(), scope=("network" + str(model_num)))
                    models.append(model)

                # register training operations on Trainer class
                trainers = []
                for model_num in range(2):
                    with tf.device("/gpu:" + str(model_num)):
                        model = models[model_num]
                        trainer = Trainer(model)
                        trainer.train_loss_op, trainer.train_accuracy_op, trainer.train_op, trainer.train_xentropy_op, trainer.train_prob_op = model.build_train_op(self.configuration.lr_boundaries, self.configuration.lr_values, self.configuration.optimizer)
                        trainer.test_loss_op, trainer.test_accuracy_op, trainer.test_xentropy_op, trainer.test_prob_op = model.build_test_op()
                        trainers.append(trainer)

                        sess.run(tf.global_variables_initializer())

                ######################## main part for pre-training #######################
                start = time.time()

                print(colored("[LOG]", "blue"),  colored(("[Pre-training procedure] starts " + str(self.configuration.total_epoch) + " epochs"), "green"))
                self.training(sess, trainers, training_log)
                print(colored("[TIME]", "magenta"), str(round(time.time() - start, 2)) + " seconds took for Phase II")
                #########################################################################################

                sess.close()

        f = open(self.configuration.log_path + "/convergence_log.csv", "w")
        for text in training_log:
            f.write(text + "\n")
        f.close()

    def training(self, sess, trainers, training_log):
        disagreement_ids = set()

        for epoch in range(self.configuration.total_epoch):

            selection_ratio = 1.0 - self.reader.noise_rate * np.fmin(1.0, float(float(epoch) + 1.0) / float(self.configuration.warm_up_epoch))

            avg_train_losses = np.zeros(len(trainers), dtype=float)
            avg_train_accs = np.zeros(len(trainers), dtype=float)
            avg_hit_ratios = np.zeros(len(trainers), dtype=float)
            avg_clean_samples = np.zeros(len(trainers), dtype=float)
            avg_disagreement_samples = 0.0

            for i in range(self.reader.train_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.train_patcher.get_next_random_mini_batch()

                # losses from model 0
                softmax_matrix_0, loss_array_0, train_loss_0, train_acc_0 = sess.run([trainers[0].train_prob_op, trainers[0].train_xentropy_op, trainers[0].train_loss_op, trainers[0].train_accuracy_op], feed_dict={trainers[0].model.train_image_placeholder: images, trainers[0].model.train_label_placeholder: labels})
                # losses from model 1
                softmax_matrix_1, loss_array_1, train_loss_1, train_acc_1 = sess.run([trainers[1].train_prob_op, trainers[1].train_xentropy_op, trainers[1].train_loss_op, trainers[1].train_accuracy_op], feed_dict={trainers[1].model.train_image_placeholder: images, trainers[1].model.train_label_placeholder: labels})

                # reduce to disagreement set
                disagreement_ids.clear()
                for j in range(len(ids)):
                    # disagreement condition
                    if np.argmax(softmax_matrix_0[j]) != np.argmax(softmax_matrix_1[j]):
                        disagreement_ids.add(ids[j])

                avg_disagreement_samples += float(len(disagreement_ids))

                # choose R(T) % small-loss instances
                ids_0, images_0, labels_0, hit_ratio_0 =  select_low_loss_samples(ids, images, labels, loss_array_0, disagreement_ids, selection_ratio, self.reader)
                ids_1, images_1, labels_1, hit_ratio_1 =  select_low_loss_samples(ids, images, labels, loss_array_1, disagreement_ids, selection_ratio, self.reader)

                # co-training
                _, _ = sess.run([trainers[0].train_op, trainers[1].train_op], feed_dict={trainers[0].model.train_image_placeholder: images_1, trainers[0].model.train_label_placeholder: labels_1,
                                                                                         trainers[1].model.train_image_placeholder: images_0, trainers[1].model.train_label_placeholder: labels_0})

                avg_train_losses[0] += train_loss_0
                avg_train_accs[0] += train_acc_0
                avg_hit_ratios[0] += hit_ratio_0
                avg_clean_samples[0]  += len(ids_0)

                avg_train_losses[1] += train_loss_1
                avg_train_accs[1] += train_acc_1
                avg_hit_ratios[1] += hit_ratio_1
                avg_clean_samples[1] += len(ids_1)


            for model_num in range(len(trainers)):
                avg_hit_ratios[model_num] /= self.reader.train_patcher.num_iters_per_epoch
                avg_clean_samples[model_num] /= self.reader.train_patcher.num_iters_per_epoch
                avg_train_losses[model_num] /= self.reader.train_patcher.num_iters_per_epoch
                avg_train_accs[model_num] /= self.reader.train_patcher.num_iters_per_epoch
            avg_disagreement_samples /= self.reader.train_patcher.num_iters_per_epoch
            #print("avg_disagreemented_samples: ", avg_disagreement_samples)

            # Validation
            avg_val_losses = np.zeros(len(trainers), dtype=float)
            avg_val_accs = np.zeros(len(trainers), dtype=float)
            for i in range(self.reader.validation_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.validation_patcher.get_eval_mini_batch(i)

                for model_num in range(len(trainers)):
                    val_loss, val_acc = sess.run([trainers[model_num].test_loss_op, trainers[model_num].test_accuracy_op], feed_dict={trainers[model_num].model.test_image_placeholder: images, trainers[model_num].model.test_label_placeholder: labels})
                    avg_val_losses[model_num] += val_loss
                    avg_val_accs[model_num] += val_acc

            for model_num in range(len(trainers)):
                avg_val_losses[model_num] /= self.reader.validation_patcher.num_iters_per_epoch
                avg_val_accs[model_num] /= self.reader.validation_patcher.num_iters_per_epoch

            # Test
            avg_test_losses = np.zeros(len(trainers), dtype=float)
            avg_test_accs = np.zeros(len(trainers), dtype=float)
            for i in range(self.reader.test_patcher.num_iters_per_epoch):
                ids, images, labels = self.reader.test_patcher.get_eval_mini_batch(i)

                for model_num in range(len(trainers)):
                    val_loss, val_acc = sess.run([trainers[model_num].test_loss_op, trainers[model_num].test_accuracy_op], feed_dict={trainers[model_num].model.test_image_placeholder: images, trainers[model_num].model.test_label_placeholder: labels})
                    avg_test_losses[model_num] += val_loss
                    avg_test_accs[model_num] += val_acc

            for model_num in range(len(trainers)):
                avg_test_losses[model_num] /= self.reader.test_patcher.num_iters_per_epoch
                avg_test_accs[model_num] /= self.reader.test_patcher.num_iters_per_epoch

            # training full log
            '''
            cur_lr = sess.run(trainers[0].model.learning_rate)
            print((epoch + 1), ", ", cur_lr, ", ", avg_train_losses[0], ", ", avg_train_losses[1],  ", ", (1.0-avg_train_accs[0]),  ", ", (1.0-avg_train_accs[1]), ", ", avg_val_losses[0], ", ", avg_val_losses[1], ", ", (1.0-avg_val_accs[0]), ", ", (1.0-avg_val_accs[1]), ", ", avg_test_losses[0], ", ", avg_test_losses[1], ", ", (1.0-avg_test_accs[0]), ", ", (1.0-avg_test_accs[1]), ", ", avg_clean_samples[0], ", ", avg_clean_samples[1], ", ", avg_hit_ratios[0], ", ", avg_hit_ratios[1])
            if training_log is not None:
                training_log.append(str(epoch + 1) + ", " + str(cur_lr) + ", " + str(avg_train_losses[0]) + ", " + str(avg_train_losses[1]) + ", " + str(1.0 - avg_train_accs[0]) + ", " + str(1.0 - avg_train_accs[1]) + ", " + str(avg_val_losses[0]) + ", " + str(avg_val_losses[1]) + ", " + str(1.0 - avg_val_accs[0]) + ", " + str(1.0 - avg_val_accs[1]) + ", " + str(avg_test_losses[0]) + ", " + str(avg_test_losses[1]) + ", " + str(1.0 - avg_test_accs[0]) + ", " + str(1.0 - avg_test_accs[1]) + ", " + str(avg_clean_samples[0]) + ", " + str(avg_clean_samples[1]) + ", " + str(avg_hit_ratios[0]) + ", " + str(avg_hit_ratios[1]))
            '''

            # training only error log
            cur_lr = sess.run(trainers[0].model.learning_rate)
            print((epoch + 1), ", ", cur_lr, ", ", avg_train_losses[0], ", ", avg_train_losses[1],  ", ", (1.0-avg_train_accs[0]),  ", ", (1.0-avg_train_accs[1]), ", ", avg_val_losses[0], ", ", avg_val_losses[1], ", ", (1.0-avg_val_accs[0]), ", ", (1.0-avg_val_accs[1]), ", ", avg_test_losses[0], ", ", avg_test_losses[1], ", ", (1.0-avg_test_accs[0]), ", ", (1.0-avg_test_accs[1]))
            if training_log is not None:
                training_log.append(str(epoch + 1) + ", " + str(cur_lr) + ", " + str(avg_train_losses[0]) + ", " + str(avg_train_losses[1]) + ", " + str(1.0 - avg_train_accs[0]) + ", " + str(1.0 - avg_train_accs[1]) + ", " + str(avg_val_losses[0]) + ", " + str(avg_val_losses[1]) + ", " + str(1.0 - avg_val_accs[0]) + ", " + str(1.0 - avg_val_accs[1]) + ", " + str(avg_test_losses[0]) + ", " + str(avg_test_losses[1]) + ", " + str(1.0 - avg_test_accs[0]) + ", " + str(1.0 - avg_test_accs[1]))


def select_low_loss_samples(ids, images, labels, loss_array, disagreement_ids, selection_ratio, reader):

    clean_ids = []
    clean_images = []
    clean_labels = []

    num_clean_instances = int(np.ceil(float(len(ids)) * selection_ratio))

    loss_map = {}
    image_map = {}
    label_map = {}

    for i in range(len(ids)):
        # disagreement condition
        if len(disagreement_ids) > 0:
            if ids[i] in disagreement_ids:
                loss_map[ids[i]] = loss_array[i]
                image_map[ids[i]] = images[i]
                label_map[ids[i]] = labels[i]
        # Exception: there is no disagreemented samples
        else:
            loss_map[ids[i]] = loss_array[i]
            image_map[ids[i]] = images[i]
            label_map[ids[i]] = labels[i]

    # sort loss by descending order
    loss_map = dict(sorted(loss_map.items(), key=operator.itemgetter(1), reverse=False))

    index = 0
    for key in loss_map.keys():
        if index < num_clean_instances:
            clean_ids.append(key)
            clean_images.append(image_map[key])
            clean_labels.append(label_map[key])
        index += 1

    # clean hit rate
    hit_rate = 0.0
    for id in clean_ids:
        if reader.train_data[id].true_label == reader.train_data[id].label:
            hit_rate += 1.0

    hit_rate /= float(len(clean_ids))

    return clean_ids, clean_images, clean_labels, hit_rate