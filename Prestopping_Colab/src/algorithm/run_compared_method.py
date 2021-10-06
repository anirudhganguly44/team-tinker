import tensorflow as tf
import os, sys
import numpy as np
from termcolor import colored
from reader import input_reader
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from algorithm.default import *
from algorithm.coteaching import *
from algorithm.coteaching_plus import *
from algorithm.selfie import *
from algorithm.activebias import *

class Configuration(object):
    pass

class ComparedMethodRunner(object):
    def __init__(self, gpu_id, dataset_name, model_name, method_name, noise_type=None, noise_rate=0.0, log_dir="log"):

        self.gpu_id = gpu_id
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.noise_type = noise_type
        self.noise_rate = noise_rate
        self.method_name = method_name
        self.log_dir = log_dir
        self.reader = None
        self.configuration = None


    def data_preparation(self):

        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.visible_device_list = str(self.gpu_id)
        config.gpu_options.allow_growth = True
        graph = tf.Graph()

        with graph.as_default():
            with tf.device('/gpu:' + str(self.gpu_id)):
                with tf.Session(config=config) as sess:

                    # assign reader
                    reader = input_reader.InputReader(self.dataset_name)
                    reader.data_load()

                    coord = tf.train.Coordinator()
                    threads = tf.train.start_queue_runners(coord = coord)

                    # initialize batch patcher: load data, noise inject, init batch pathcer.
                    reader.init_batch_patcher(sess, self.noise_type, self.noise_rate)

                    coord.request_stop()
                    coord.join(threads)
                    sess.close()

            self.reader = reader

    def set_training_configuration(self, total_epoch=100, warm_up_epoch=25, batch_size=128, lr_values=[0.1, 0.02, 0.004], lr_boundaries=[50, 75], optimizer="momentum"):

        self.configuration = Configuration()
        self.configuration.gpu_id = self.gpu_id
        self.configuration.method_name = self.method_name
        self.configuration.model_name = self.model_name
        self.configuration.total_epoch = total_epoch
        self.configuration.warm_up_epoch = warm_up_epoch
        self.configuration.optimizer = optimizer
        self.reader.set_batch_size(batch_size)

        # lr_boundaries rescaling for iterations
        if len(lr_values) - 1 != len(lr_boundaries):
            print(colored("[ERROR]", "red"), "LR scheduling is not properly specified")
            print(colored("[ERROR]", "red"), "E.g., ) If you want to decay the initial learning rate 0.1 to 0.01 at 50 epochs")
            print(colored("[ERROR]", "red"), "E.g., ) Set lr_values = [0.1, 0.01] and lr_boundaries = [50]")
            sys.exit(1)

        # method availability check
        if self.method_name not in ["Default", "Coteaching", "CoteachingPlus", "ActiveBias", "SELFIE"]:
            print(colored("[ERROR]", "red"), "Not available method that must be in [Default, ActiveBias, Coteaching, CoteachingPlus, SELFIE]")
            sys.exit(1)

        temp = []
        for i in range(len(lr_boundaries)):
            temp.append(lr_boundaries[i] * self.reader.train_patcher.num_iters_per_epoch)

        self.configuration.lr_values = lr_values
        self.configuration.lr_boundaries = temp

        # log path
        dir_header = "/" + self.dataset_name + "/" + self.model_name + "/" + str(self.noise_type) + "/" + str(self.noise_rate)

        # phase I log path
        self.configuration.log_path = self.log_dir + "/" + self.method_name + "/" + dir_header

        if not os.path.exists(self.configuration.log_path):
            os.makedirs(self.configuration.log_path)


        print(colored("[LOG]", "blue"), colored("Training configuration set up", "green"))
        print(colored("[LOG]", "blue"), "log directory path: ", "\"" + self.configuration.log_path + "\"")
        print(colored("[LOG]", "blue"), "Method name: ", self.configuration.method_name)
        print(colored("[LOG]", "blue"), "Model name: ", self.configuration.model_name)
        print(colored("[LOG]", "blue"), "Optimizer ", self.configuration.optimizer)


    def train(self):
        print(colored("[LOG]", "blue"), colored("[Phase I] Pre-trains " + self.model_name + " using " + self.method_name, "green"))

        if self.method_name == "Default":
            method = Default(self.reader, self.configuration)
        elif self.method_name == "ActiveBias":
            method = ActiveBias(self.reader, self.configuration, smoothness=0.2)
        elif self.method_name == "Coteaching":
            method = Coteaching(self.reader, self.configuration)
        elif self.method_name == "CoteachingPlus":
            method = CoteachingPlus(self.reader, self.configuration)
        elif self.method_name == "SELFIE":
            method = SELFIE(self.reader, self.configuration, queue_size=15, threshold=0.05, restart=3)

        method.train()

    def get_header_str(self):
        return self.dataset_name + "_" + self.method_name + "_" + self.model_name + "_" + self.noise_type + "_" + str(self.noise_rate)

    def run(self, total_epoch=120, warm_up_epoch=25, batch_size=128, lr_values=[0.1, 0.02, 0.004], lr_boundaries=[60, 90], optimizer="momentum"):
        self.data_preparation()
        self.set_training_configuration(total_epoch=total_epoch, warm_up_epoch=warm_up_epoch, batch_size=batch_size, lr_values=lr_values, lr_boundaries=lr_boundaries, optimizer=optimizer)
        self.train()


