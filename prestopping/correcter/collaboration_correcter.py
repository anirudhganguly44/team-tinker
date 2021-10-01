import numpy as np
from structure.minibatch import *
from structure.sample import *
from PIL import Image
import matplotlib.pyplot as plt
import os, math, sys


class Correcter(object):
    def __init__(self, reader, queue_size=15, threshold=0.05):

        self.size_of_data = reader.get_num_training()
        self.num_of_classes = reader.get_num_labels()
        self.queue_size = queue_size
        self.threshold = threshold
        self.reader = reader

        # prediction histories of samples
        self.all_predictions = {}
        for i in range(self.size_of_data):
            self.all_predictions[i] = np.zeros(queue_size, dtype=int)

        # Max Correctablility
        self.max_certainty = -np.log(1.0/float(self.num_of_classes))

        # Corrected label map
        self.corrected_labels = {}
        for i in range(self.size_of_data):
            self.corrected_labels[i] = -1

        self.update_counters = np.zeros(self.size_of_data, dtype=int)

    def async_update_prediction_matrix(self, ids, softmax_matrix):
        for i in range(len(ids)):
            id = ids[i]
            predicted_label = np.argmax(softmax_matrix[i])
            # append the predicted label to the prediction matrix
            cur_index = self.update_counters[id] % self.queue_size
            self.all_predictions[id][cur_index] = predicted_label
            self.update_counters[id] += 1

    def get_clean_batch(self, ids, images, labels):

        clean_batch = MiniBatch()

        for i in range(len(ids)):
            if self.reader.trustnesses[ids[i]]:
                clean_batch.append(ids[i], images[i], labels[i])

        return clean_batch


    def get_corrected_samples(self, ids, images):
        corrected_batch = MiniBatch()

        # check correctability for each sample
        accumulator = {}
        for i in range(len(ids)):
            id = ids[i]
            image = images[i]

            if self.update_counters[id] >= self.queue_size:
                predictions = self.all_predictions[id]
            else:
                predictions = np.zeros(self.update_counters[id], dtype=int)
                for j in range(self.update_counters[id]):
                    predictions[j] = self.all_predictions[id][j]
            accumulator.clear()

            for prediction in predictions:
                if prediction not in accumulator:
                    accumulator[prediction] = 1
                else:
                    accumulator[prediction] = accumulator[prediction] + 1

            p_dict = np.zeros(self.num_of_classes, dtype=float)
            for key, value in accumulator.items():
                p_dict[key] = float(value) / float(self.queue_size)

            # based on entropy
            negative_entropy = 0.0
            for i in range(len(p_dict)):
                if p_dict[i] == 0:
                    negative_entropy += 0.0
                else:
                    negative_entropy += p_dict[i] * np.log(p_dict[i])
            certainty = - negative_entropy / self.max_certainty

            if certainty <= self.threshold:
                self.corrected_labels[id] = np.argmax(p_dict)
                corrected_batch.append(id, image, self.corrected_labels[id])

            #reuse
            elif self.corrected_labels[id] != -1:
                corrected_batch.append(id, image, self.corrected_labels[id])

        return corrected_batch

    def compute_uncertainty(self, id):
        # check correctability for each sample
        accumulator = {}

        if self.update_counters[id] >= self.queue_size:
            predictions = self.all_predictions[id]
        else:
            predictions = np.zeros(self.update_counters[id], dtype=int)
            for j in range(self.update_counters[id]):
                predictions[j] = self.all_predictions[id][j]
        accumulator.clear()

        for prediction in predictions:
            if prediction not in accumulator:
                accumulator[prediction] = 1
            else:
                accumulator[prediction] = accumulator[prediction] + 1

        p_dict = np.zeros(self.num_of_classes, dtype=float)
        for key, value in accumulator.items():
            p_dict[key] = float(value) / float(self.queue_size)

        # based on entropy
        negative_entropy = 0.0
        for i in range(len(p_dict)):
            if p_dict[i] == 0:
                negative_entropy += 0.0
            else:
                negative_entropy += p_dict[i] * np.log(p_dict[i])
        certainty = - negative_entropy / self.max_certainty
        return certainty

    def save_images_orig(self, path):
        for index in range(len(self.reader.train_data)):
            sample = self.reader.train_data[index]
            if sample == None: continue
            label = self.corrected_labels[sample.id]
            if label == -1: continue
            if sample.label == sample.true_label: continue

            if label == sample.true_label:
                print(f"label is correct for: {sample.img_name}")
                full_path = os.path.join("C:\\sjsu", path, "good")
                if os.path.exists(full_path) == False:
                    os.mkdir(full_path)
                image_name = f"{sample.id}_Wrong{sample.label}_Corrected{label}.png"
                img_path = os.path.join(full_path, image_name)
                #sample.orig_image.save(img_path)
                img = sample.orig_image.astype(np.uint8)
                plt.imsave(img_path, img)
            else:
                print(f"label is wrong for: {sample.img_name}")
                full_path = os.path.join("C:\\sjsu", path, "bad")
                if os.path.exists(full_path) == False:
                    os.mkdir(full_path)
                image_name = f"{sample.id}_Wrong{sample.label}_Corrected{label}_True{sample.true_label}.png"
                img_path = os.path.join(full_path, image_name)
                #sample.orig_image.save(img_path)
                img = sample.orig_image.astype(np.uint8)
                plt.imsave(img_path, img)

    def merge_clean_and_corrected_samples(self, clean_batch, corrected_batch, priority="clean"):

        final_batch = MiniBatch()
        batch_ids = set()

        num_corrected = 0.0
        num_clean = 0.0
        correct_hit_rate = 0.0
        clean_hit_rate = 0.0

        if priority == "correction":
            # Add correct batch
            for i in range(len(corrected_batch.ids)):
                batch_ids.add(corrected_batch.ids[i])
                final_batch.append(corrected_batch.ids[i], corrected_batch.images[i], corrected_batch.labels[i])

                if self.reader.train_data[corrected_batch.ids[i]].true_label == corrected_batch.labels[i]:
                    correct_hit_rate += 1.0
                num_corrected += 1

            # Add clean batch
            for i in range(len(clean_batch.ids)):

                if clean_batch.ids[i] in batch_ids:
                    continue

                if self.corrected_labels[clean_batch.ids[i]] == -1:
                    final_batch.append(clean_batch.ids[i], clean_batch.images[i], clean_batch.labels[i])

                    if self.reader.train_data[clean_batch.ids[i]].true_label == self.reader.train_data[clean_batch.ids[i]].label:
                        clean_hit_rate += 1.0
                    num_clean += 1

                elif self.corrected_labels[clean_batch.ids[i]] != -1:
                    final_batch.append(clean_batch.ids[i], clean_batch.images[i], self.corrected_labels[clean_batch.ids[i]])

                    if self.reader.train_data[clean_batch.ids[i]].true_label == self.corrected_labels[clean_batch.ids[i]]:
                        correct_hit_rate += 1.0
                    num_corrected += 1

        elif priority == "clean":
            # Add clean batch
            for i in range(len(clean_batch.ids)):
                batch_ids.add(clean_batch.ids[i])

                if self.reader.trustnesses[clean_batch.ids[i]] or self.corrected_labels[clean_batch.ids[i]] == -1:
                    label = clean_batch.labels[i]
                    final_batch.append(clean_batch.ids[i], clean_batch.images[i], label)
                else:
                    label = self.corrected_labels[clean_batch.ids[i]]
                    final_batch.append(clean_batch.ids[i], clean_batch.images[i], label)

                if self.reader.train_data[clean_batch.ids[i]].true_label == label:
                    clean_hit_rate += 1.0
                num_clean += 1

            # Add corrected batch
            for i in range(len(corrected_batch.ids)):

                if corrected_batch.ids[i] in batch_ids:
                    continue

                final_batch.append(corrected_batch.ids[i], corrected_batch.images[i], corrected_batch.labels[i])

                if self.reader.train_data[corrected_batch.ids[i]].true_label == corrected_batch.labels[i]:
                    correct_hit_rate += 1.0
                num_corrected += 1

        if num_corrected == 0:
            correct_hit_rate = 1.0
        else:
            correct_hit_rate /= float(num_corrected)

        if num_clean == 0:
            clean_hit_rate = 1.0
        else:
            clean_hit_rate /= float(num_clean)

        return final_batch.ids, final_batch.images, final_batch.labels, num_clean, num_corrected, clean_hit_rate, correct_hit_rate

    def patch_clean_with_corrected_sample_batch(self, ids, images, labels):
        # 1. get clean
        clean_batch = self.get_clean_batch(ids, images, labels)
        # 2. get corrected samples
        corrected_batch = self.get_corrected_samples(ids, images)
        # 3. merging
        ids, images, labels, num_clean, num_corrected, clean_hit_rate, correct_hit_rate = self.merge_clean_and_corrected_samples(clean_batch, corrected_batch)
        return ids, images, labels, num_clean, num_corrected, clean_hit_rate, correct_hit_rate

    def predictions_clear(self):
        self.all_predictions.clear()
        for i in range(self.size_of_data):
            self.all_predictions[i] = np.zeros(self.queue_size, dtype=int)