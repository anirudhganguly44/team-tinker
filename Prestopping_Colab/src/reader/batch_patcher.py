import math
import numpy as np
from termcolor import colored
from structure.minibatch import *
from structure.sample import *

'''
Class that provides batch selection functions on the finally constructed training & test dataset
'''
class BatchPatcher(object):
    def __init__(self, loaded_data, batch_size, replacement = False):
        # Assign data
        self.loaded_data = loaded_data
        self.size_of_data = len(loaded_data)

        # Setup meta info for training
        self.batch_size = batch_size
        self.num_iters_per_epoch = int(math.ceil(float(self.size_of_data) / float(self.batch_size)))

        # Replacement in mini-batch for random batch selection
        self.replacement = replacement

        print(colored("[LOG]", "blue"), "[Train patcher] # training samples:", self.size_of_data, "# iters per epoch:", self.num_iters_per_epoch)

    def set_batch_size(self, batch_size):
        self.batch_size = batch_size
        self.num_iters_per_epoch = int(math.ceil(float(self.size_of_data) / float(self.batch_size)))


    # Randomly select next mini-batch samples
    def get_next_random_mini_batch(self):
        selected_sample_ids = np.random.choice(self.size_of_data, self.batch_size, self.replacement)

        # Fetch mini-batch samples from loaded_data in main memory
        mini_batch = MiniBatch()
        for id in selected_sample_ids:
            sample = self.loaded_data[id]
            mini_batch.append(sample.id, sample.image, sample.label)

        return mini_batch.ids, mini_batch.images, mini_batch.labels

    #Iterate all training samples sequentially to evaluate the loss and error
    def get_eval_mini_batch(self, init_id):
        # init_id from 0~self.num_iters_per_epoch
        selected_sample_ids = list(range(init_id*self.batch_size, init_id*self.batch_size + self.batch_size))

        # Fetch mini-batch samples from loaded_data in main memory
        mini_batch = MiniBatch()
        for id in selected_sample_ids:
            if id >= self.size_of_data:
                continue
            else:
                sample = self.loaded_data[id]
                mini_batch.append(sample.id, sample.image, sample.label)

        return mini_batch.ids, mini_batch.images, mini_batch.labels