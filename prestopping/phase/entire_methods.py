import tensorflow as tf
import os, sys
from termcolor import colored
from reader import input_reader
from network.DenseNet.DenseNet import *
from network.VGG.VGG19 import *
from phase.phase_I_earlystopping import *
from phase.phase_II_remaining_learning import *
from phase.phase_III_refurbishment import *

class Configuration(object):
    pass

class TwoPhaseMethod(object):
    def __init__(self, gpu_id, dataset_name, model_name, method_name, noise_type=None, noise_rate=0.0, log_dir="log", custom_dir=""):

        self.gpu_id = gpu_id
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.noise_type = noise_type
        self.noise_rate = noise_rate
        self.method_name = method_name
        self.log_dir = log_dir
        self.reader = None
        self.configuration = None
        self.custom_dir = custom_dir


    def data_preparation(self):

        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.visible_device_list = str(self.gpu_id)
        config.gpu_options.allow_growth = True
        graph = tf.Graph()

        with graph.as_default():
            with tf.device('/gpu:' + str(self.gpu_id)):
                with tf.Session(config=config) as sess:

                    # assign reader
                    reader = input_reader.InputReader(self.dataset_name, self.custom_dir)
                    if(self.dataset_name != "custom" and self.dataset_name != "scan"):
                        reader.data_load()

                    coord = tf.train.Coordinator()
                    threads = tf.train.start_queue_runners(coord = coord)

                    # initialize batch patcher: load data, noise inject, init batch pathcer.
                    reader.init_batch_patcher(sess, self.noise_type, self.noise_rate, self.dataset_name)

                    coord.request_stop()
                    coord.join(threads)
                    sess.close()

            self.reader = reader

    def set_training_configuration(self, total_epoch=100, warm_up_epoch=25, batch_size=128, lr_values=[0.1, 0.02, 0.004], lr_boundaries=[50, 75], optimizer="momentum", queue_size=10):

        self.configuration = Configuration()
        self.configuration.gpu_id = self.gpu_id
        self.configuration.method_name = self.method_name
        self.configuration.model_name = self.model_name
        self.configuration.total_epoch = total_epoch
        self.configuration.total_iteraton = total_epoch * self.reader.train_patcher.num_iters_per_epoch
        self.configuration.warm_up_epoch = warm_up_epoch
        self.configuration.optimizer = optimizer
        self.configuration.queue_size = queue_size
        self.reader.set_batch_size(batch_size)

        # lr_boundaries rescaling for iterations
        if len(lr_values) - 1 != len(lr_boundaries):
            print(colored("[ERROR]", "red"), "LR scheduling is not properly specified")
            print(colored("[ERROR]", "red"), "E.g., ) If you want to decay the initial learning rate 0.1 to 0.01 at 50 epochs")
            print(colored("[ERROR]", "red"), "E.g., ) Set lr_values = [0.1, 0.01] and lr_boundaries = [50]")
            sys.exit(1)

        # method availability check
        if self.method_name not in ["Prestopping", "PrestoppingPlus"]:
            print(colored("[ERROR]", "red"), "Not available method that must be in [Prestopping, PrestoppingPlus]")
            sys.exit(1)

        temp = []
        for i in range(len(lr_boundaries)):
            temp.append(lr_boundaries[i] * self.reader.train_patcher.num_iters_per_epoch)

        self.configuration.lr_values = lr_values
        self.configuration.lr_boundaries = temp

        # log path
        dir_header = "/" + self.dataset_name + "/" + self.model_name + "/" + str(self.noise_type) + "/" + str(self.noise_rate)

        # phase I log path
        self.configuration.pretrain_path = self.log_dir + "/phase_I_early_stop" + dir_header

        if not os.path.exists(self.configuration.pretrain_path):
            os.makedirs(self.configuration.pretrain_path)

        # phase II log path
        self.configuration.extracting_path = self.log_dir + "/phase_II_remaining_learning" + dir_header

        if not os.path.exists(self.configuration.extracting_path):
            os.makedirs(self.configuration.extracting_path)

        # phase III log path
        self.configuration.collaboration_path = self.log_dir + "/phase_III_refurbishment/" + self.method_name + "/" + self.dataset_name + "/" + self.model_name + "/" + str(self.noise_type) + "/" + str(self.noise_rate)

        if not os.path.exists(self.configuration.collaboration_path):
            os.makedirs(self.configuration.collaboration_path)

        print(colored("[LOG]", "blue"), colored("Training configuration set up", "green"))
        print(colored("[LOG]", "blue"), "Phase I ``early stopping`` log directory path: ", "\"" + self.configuration.pretrain_path + "\"")
        print(colored("[LOG]", "blue"), "Phase II ``learning from a maximal safe set`` log directory path: ", "\"" + self.configuration.extracting_path + "\"")
        print(colored("[LOG]", "blue"), "Phase III ``Prestopping+ (if configured)`` log directory path: ", "\"" + self.configuration.collaboration_path + "\"")
        print(colored("[LOG]", "blue"), "Method name: ", self.configuration.method_name)
        print(colored("[LOG]", "blue"), "Model name: ", self.configuration.model_name)
        print(colored("[LOG]", "blue"), "Optimizer ", self.configuration.optimizer)


    def phaseI_earlystop(self):
        print(colored("[LOG]", "blue"), colored("[Phase I] Pre-trains " + self.model_name + " using " + self.method_name, "green"))

        if os.path.exists(self.configuration.pretrain_path + "/phase_I_convergence_log.csv") and os.path.exists(self.configuration.pretrain_path + "/history_backup") and os.path.exists(self.configuration.pretrain_path + "/saved"):
            print(colored("[LOG]", "blue"), "Pre-trained model is already exist. Thus reuse them")
        else:
            method = Phase_I(self.reader, self.configuration)
            method.pretrain()

        # summary about best test error and epoch.
        _, _, self.configuration.stopped_val_error, self.configuration.phase_I_min_test_error = self.reader.load_pretraiend_summary(self.configuration.pretrain_path + "/phase_I_convergence_log.csv", log=True)

        phase_I_best_val_error = self.configuration.stopped_val_error
        phase_I_best_test_error = self.configuration.phase_I_min_test_error

        return phase_I_best_val_error, phase_I_best_test_error

    def phaseII_training_on_maxmal_safe_set(self):

        print(colored("[LOG]", "blue"), colored("[Phase II] Extracts trusted samples", "green"))
        extracter = Phase_II(self.reader, self.configuration, self.configuration.pretrain_path)

        trusted_sample_path = self.configuration.extracting_path + "/trusted_samples.csv"
        convergence_path = self.configuration.extracting_path + "/phase_II_convergence_log.csv"
        if os.path.exists(trusted_sample_path) and os.path.exists(convergence_path):
            self.reader.load_stable_samples(trusted_sample_path)
            print(colored("[LOG]", "blue"), "Extracting samples are already exist. Thus reuse them")
            print(colored("[LOG]", "blue"), "Load trusted samples from", "\"" + (trusted_sample_path + "\""))
        else:
            self.reader.print_confusion_matrix()
            extracter.stable_training()
            self.reader.load_stable_samples(trusted_sample_path)

        _, _, self.configuration.phase_II_min_val_error , self.configuration.phase_II_min_test_error = self.reader.load_pretraiend_summary(self.configuration.extracting_path + "/phase_II_convergence_log.csv")

        return self.configuration.phase_II_min_val_error,  self.configuration.phase_II_min_test_error

    def phaseIII_refurbishment(self):

        print(colored("[LOG]", "blue"), colored("[Phase III] retraining the model using trusted samples with sota algorithm", "green"))

        if self.method_name == "Prestopping":
            return self.configuration.phase_II_min_val_error, self.configuration.phase_II_min_test_error
        elif self.method_name == "PrestoppingPlus":
            method = Phase_III(self.reader, self.configuration)
        method.train_by_selfie()

        _, _, self.configuration.phase_III_min_val_error , self.configuration.phase_III_min_test_error = self.reader.load_pretraiend_summary(self.configuration.collaboration_path + "/phase_III_convergence_log.csv")

        phase_III_best_val_error = self.configuration.phase_III_min_val_error
        phase_III_best_test_error = self.configuration.phase_III_min_test_error

        return phase_III_best_val_error, phase_III_best_test_error


    def get_header_str(self):
        return self.dataset_name + "_" + self.method_name + "_" + self.model_name + "_" + self.noise_type + "_" + str(self.noise_rate)

    def run_all_phases(self, total_epoch=120, warm_up_epoch=25, batch_size=128, queue_size=10, lr_values=[0.1, 0.02, 0.004], lr_boundaries=[60, 90], optimizer="momentum"):

        self.data_preparation()
        self.set_training_configuration(total_epoch=total_epoch, warm_up_epoch=warm_up_epoch, batch_size=batch_size, queue_size=queue_size, lr_values=lr_values, lr_boundaries=lr_boundaries, optimizer=optimizer)

        # for Prestopping algorithm
        self.phaseI_earlystop()
        self.phaseII_training_on_maxmal_safe_set()

        # for PrestoppingPlus algorithm
        if self.method_name == "PrestoppingPlus":
            self.phaseIII_refurbishment()


