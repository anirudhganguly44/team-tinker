import sys, math, os.path, time
import tensorflow as tf
import numpy as np
from termcolor import colored
from reader.input_meta import *
from reader.modified_tf_functions import *
from reader.batch_patcher import *
from structure.minibatch import *
from structure.sample import *

ID_BYTES = 4
LABEL_BYTES = 4

class InputReader(object):
    def __init__(self, dataset_name, batch_size=128):

        # check data existance
        if dataset_name == "CIFAR-10":
            self.meta = CIFAR10_META
        elif dataset_name == "CIFAR-100":
            self.meta = CIFAR100_META
        elif dataset_name == "Tiny-ImageNet":
            self.meta = TinyImageNet_Meta
        elif dataset_name == "ANIMAL-10N":
            self.meta = ANIMAL10N_META
        elif dataset_name == "Clothings-70K":
            self.meta = CLOTHINGS70K_META
        elif dataset_name == "Food-101N":
            self.meta = FOOD101N_META
        else:
            print(colored("[ERROR]", "red"), "The data named ", dataset_name, "is not exist.")
            sys.exit(1)

        self.dataset_name = dataset_name

        # data reader: tensorflow graph function to read
        self.batch_size = batch_size
        self.data_reader = None

        # loaded data
        self.train_data = None
        self.validation_data = None
        self.test_data = None

        # batch patcher
        self.train_patcher = None
        self.validation_patcher = None
        self.test_patcher = None

    def data_load(self):
        self.data_reader = DataReader(self.meta, self.batch_size)

    # this function must be called after following two tf functions:
    # (i) coord = tf.train.Coordinator()
    # (ii) threads = tf.train.start_queue_runners(coord=coord)
    def init_batch_patcher(self, sess, noise_type="None", noise_rate=0.0):
        start = time.time()
        # load all in-and-out context data
        print(colored("[LOG]", "blue"), colored("Loads " + self.meta["name"] + " in main memory", "green"))
        self.load_all_data(sess)

        # noise injection
        print(colored("[LOG]", "blue"), colored("Injects noise into training data", "green"))
        self.noise_injection(noise_type=noise_type, noise_rate=noise_rate)
        self.print_confusion_matrix()

        # setup batch patcher
        print(colored("[LOG]", "blue"), colored("Registers batch patcher", "green"))
        self.train_patcher = BatchPatcher(self.train_data, self.batch_size, replacement=False)
        self.validation_patcher = BatchPatcher(self.validation_data, self.batch_size, replacement=False)
        self.test_patcher = BatchPatcher(self.test_data, self.batch_size, replacement=False)
        print(colored("[TIME]", "magenta"), str(round(time.time()-start,2)) + " seconds took for initializing input reader")


    def get_input_shape(self):
        if self.meta["resize"] is None:
            return self.meta["shape"]
        else:
            return self.meta["resize"]

    def get_num_labels(self):
        return self.meta["num_labels"]

    def get_num_training(self):
        return len(self.train_data)

    def get_num_test(self):
        return len(self.test_data)

    def set_batch_size(self, batch_size):
        self.batch_size = batch_size
        self.train_patcher.set_batch_size(batch_size)
        self.test_patcher.set_batch_size(batch_size)

    def print_confusion_matrix(self, log=None):
        log_str = ""
        print(colored("[LOG]", "blue"), colored("Prints confusion matrix:", "green"))
        confusion_matrix = self.compute_confusion_matrix()
        for i in range(len(confusion_matrix)):
            for j in range(len(confusion_matrix[i])):
                if j == 0:
                    print(colored("[LOG]", "blue"), str(confusion_matrix[i][j]) + " ", end=',')
                else:
                    print(str(confusion_matrix[i][j]) + " ", end=',')
                log_str += str(confusion_matrix[i][j]) + ", "
            print("")
            log_str += "\n"
        log_str += "\n"
        if log is not None:
            log.append(log_str)

    def load_pretraiend_summary(self, existing_path, log=False):

        min_val_error = 1.0
        target_epoch = -1
        target_lr = 0.0

        min_test_error = 1.0

        for line in open(existing_path, "r"):
            toks = line.rstrip().split(",")
            epoch = int(toks[0].strip())
            lr = float(toks[1].strip())
            val_error = float(toks[5].strip())
            test_error = float(toks[7].strip())

            if min_val_error >= val_error:
                target_epoch = epoch
                target_lr = lr
                min_val_error = val_error

            if min_test_error >= test_error:
                min_test_error = test_error

        if log:
            print(colored("[LOG]", "blue"), "Best pre-trained error was achieved at \"epoch=" + str(target_epoch) +"\", \"lr=" + str(target_lr) + "\", \"val error=" + str(min_val_error) +"\"")

        return target_epoch, target_lr, min_val_error, min_test_error

    def load_stable_samples(self, existing_path):

        self.trustnesses = np.zeros(self.get_num_training(), dtype=bool)
        true_trusted = 0
        total_trusted = 0

        # load meta
        for line in open(existing_path, "r"):
            toks = line.rstrip().split(",")
            id = int(toks[0].strip())
            noisy_label = int(toks[1].strip())
            decision = int(toks[2].strip())

            # set noisy label
            self.train_data[id].label = noisy_label

            # set decision
            if decision == 0:
                self.trustnesses[id] = True
                total_trusted += 1
                if self.train_data[id].label == self.train_data[id].true_label:
                    true_trusted += 1
            else:
                self.trustnesses[id] = False

        print(colored("[LOG]", "blue"), "Loads", total_trusted, "(" + str(true_trusted) + ")", "total (true-labeled) trusted samples from ")

    def construct_fine_tune_batch(self):
        self.train_patcher = BatchPatcher(self.trusted_data, self.batch_size, replacement=False)

    #####################################################################################################################################
    # Below functions are low-level code, you don't need to call these two functions because you can run all those code by 'init_batch_patcher'.
    def load_all_data(self, sess):
        self.train_data = self.data_reader.load_train_data(sess)
        self.validation_data = self.data_reader.load_validation_data(sess)
        self.test_data = self.data_reader.load_test_data(sess)

    def noise_injection(self, noise_type="None", noise_rate=0.0):
        if noise_type != "Symmetric" and noise_type != "Pair" and noise_type != "None":
            print(colored("[ERROR]", "red"), "Noise type must be chosen from [Pair, Symmetric, None]")
            sys.exit(1)

        self.noise_type = noise_type
        self.noise_rate = noise_rate
        print(colored("[LOG]", "blue"), "Noise type:", noise_type, ", Noise rate:", noise_rate)
        self.transition_matrix = []

        # init noise transition matrix
        for i in range(self.get_num_labels()):
            self.transition_matrix.append([])
            for j in range(self.get_num_labels()):
                self.transition_matrix[i].append(0.0)

        if noise_type == "Symmetric":
            for i in range(self.get_num_labels()):
                for j in range(self.get_num_labels()):
                    if i == j:
                        self.transition_matrix[i][j] = 1.0 - noise_rate
                    else:
                        self.transition_matrix[i][j] = noise_rate / float(self.get_num_labels() - 1)

        elif noise_type == "Pair":
            for i in range(self.get_num_labels()):
                self.transition_matrix[i][(i + 1) % self.get_num_labels()] = noise_rate
                for j in range(self.get_num_labels()):
                    if i == j:
                        self.transition_matrix[i][j] = 1.0 - noise_rate

        elif noise_type == "None":
            return

        for sample in self.train_data:
            sample.label = self.get_noise_label(self.transition_matrix[sample.true_label])
            if sample.label != sample.true_label: #  if mislabeled
                sample.type = 1 # 0: clean (default), 1: mislabeled

    def get_noise_label(self, transition_array):
        return np.random.choice(self.get_num_labels(), 1, True, p=transition_array)[0]

    def compute_confusion_matrix(self):
        noise_matrix = np.zeros([self.get_num_labels(), self.get_num_labels()], dtype = int)
        for sample in self.train_data:
            noise_matrix[sample.true_label][sample.label] += 1
        return noise_matrix
    #####################################################################################################################################

#########################################################################################################################################
# Below classes are low-level classes, you don't need to call them
class Reader(object):
    """Super Class"""
    def __init__(self, meta, batch_size):
        self.meta = meta
        self.record_bytes = ID_BYTES + LABEL_BYTES + meta["shape"][0] * meta["shape"][1] * meta["shape"][2]
        self.batch_size = batch_size

    def parse_image(self, files):
        record = Record()
        reader = tf.compat.v1.FixedLengthRecordReader(record_bytes=self.record_bytes)
        file_name, value = reader.read(files)

        byte_record = tf.compat.v1.decode_raw(value, tf.uint8)

        image_id = tf.strided_slice(byte_record, [0], [ID_BYTES])
        image_label = tf.strided_slice(byte_record, [ID_BYTES], [ID_BYTES + LABEL_BYTES])
        array_image = tf.strided_slice(byte_record, [ID_BYTES + LABEL_BYTES], [self.record_bytes])

        depth_major_image = tf.reshape(array_image, [self.meta["shape"][2], self.meta["shape"][0], self.meta["shape"][0]])
        record.image = tf.transpose(depth_major_image, [1, 2, 0])

        record.id = image_id
        record.label = image_label

        return record

    def inputs(self, filenames, normalize=True):

        # check file existance
        for filename in filenames:
            if not os.path.isfile(filename):
                print(colored("[ERROR]", "red"), "File", filename, "does not exist")
                sys.exit(1)

        print(colored("[LOG]", "blue"), "Now read following files:", filenames)

        filename_queue = tf.compat.v1.train.string_input_producer(filenames, shuffle=False)
        record = self.parse_image(filename_queue)

        # Type casting for nomalization
        record.image = tf.cast(record.image, tf.float32)

        # Resize
        if self.meta["resize"] is not None:
            record.image = tf.image.resize_images(record.image, [self.meta["resize"][0], self.meta["resize"][1]])
            print(colored("[Log]", "blue"), "Image resize:", self.meta["shape"], "->", self.meta["resize"])

        # Normalization
        if normalize:
            record.image = tf.image.per_image_standardization(record.image)

        record.id.set_shape([4, ])
        record.label.set_shape([4, ])

        return record.id, record.image, record.label

    def read(self, files, total_size, normalize=True, shuffle=False):
        t_id, t_image, t_label = self.inputs(files, normalize=normalize)
        return generate_image_and_label_batch(t_id, t_image, t_label, self.batch_size, total_size, 0.4, 16, shuffle=shuffle)

    def bulk_load_in_memory(self, sess, read_fuctions, total_size, log=""):

        num_iters_per_epoch = int(math.ceil(float(total_size) / float(self.batch_size)))

        # initialization
        loaded_data = []

        for i in range(total_size):
            loaded_data.append(None)

        # load data set in memory
        set_test = set()
        for i in range(num_iters_per_epoch):
            mini_ids, mini_images, mini_labels = sess.run([read_fuctions[0], read_fuctions[1], read_fuctions[2]])

            for j in range(self.batch_size):
                id = bytes_to_int(mini_ids[j])

                if not id in set_test:
                    loaded_data[id] = Sample(id, mini_images[j], bytes_to_int(mini_labels[j]))
                    set_test.add(id)

        print(colored("[LOG]", "blue"), ("Finished to load # of "+log+" samples:"), len(loaded_data))
        return  loaded_data

class DataReader(Reader):
    def __init__(self,  meta, batch_size):
        super().__init__(meta, batch_size)
        self.f_train = self.get_read_train_f()
        self.f_validation = self.get_read_validation_f()
        self.f_test = self.get_read_test_f()

    def get_read_train_f(self):
        files = []
        for filename in self.meta["train_files"]:
            files.append(self.meta["path"] + "/" + filename)
        ids, images, labels = self.read(files, self.meta["num_train"])
        return [ids, images, labels]

    def get_read_validation_f(self):
        files = []
        for filename in self.meta["validation_files"]:
            files.append(self.meta["path"] + "/" + filename)
        ids, images, labels = self.read(files, self.meta["num_validation"])
        return [ids, images, labels]

    def get_read_test_f(self):
        files = []
        for filename in self.meta["test_files"]:
            files.append(self.meta["path"] + "/" + filename)

        ids, images, labels = self.read(files, self.meta["num_test"])
        return [ids, images, labels]

    def load_train_data(self, sess):
        return self.bulk_load_in_memory(sess, self.f_train, self.meta["num_train"], "training")

    def load_validation_data(self, sess):
        return self.bulk_load_in_memory(sess, self.f_validation, self.meta["num_validation"], "validation")

    def load_test_data(self, sess):
        return self.bulk_load_in_memory(sess, self.f_test, self.meta["num_test"], "test")


class Record(object):
    pass

def bytes_to_int(bytes_array):
    result = 0
    for b in bytes_array:
        result = result * 256 + int(b)
    return result

#########################################################################################################################################