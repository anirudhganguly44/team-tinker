import numpy as np
from termcolor import colored

class History(object):
    def __init__(self, reader, queue_size=10, correcter=None):
        self.size_of_data = reader.get_num_training()
        self.num_of_classes = reader.get_num_labels()
        self.queue_size = queue_size
        self.reader = reader
        self.correcter = correcter

        # prediction histories of samples
        self.all_predictions = {}

        for i in range(self.size_of_data):
            self.all_predictions[i] = np.zeros(queue_size, dtype=int)

        self.update_counters = np.zeros(self.size_of_data, dtype=int)

        print(colored("[LOG]", "blue"), colored("History structure was enrolled", "green"))
        print(colored("[LOG]", "blue"), "queue size: ", self.queue_size)

    def async_update_prediction_matrix(self, ids, softmax_matrix):
        for i in range(len(ids)):
            id = ids[i]
            predicted_label = np.argmax(softmax_matrix[i])

            # append the predicted label to the prediction matrix
            cur_index = self.update_counters[id] % self.queue_size

            self.all_predictions[id][cur_index] = predicted_label
            self.update_counters[id] += 1

    def compute_decision_for_batch(self, ids):

        decisions = np.zeros(len(ids), dtype=bool)
        scores  = np.zeros(len(ids), dtype=float)

        for i in range(len(ids)):
            id = ids[i]

            if self.update_counters[id] >= self.queue_size:
                predictions = self.all_predictions[id]
            else:
                predictions = np.zeros(self.update_counters[id], dtype=int)
                for j in range(self.update_counters[id]):
                    predictions[j] = self.all_predictions[id][j]

            acc = np.zeros(self.num_of_classes, dtype=float)
            for label in predictions:
                acc[int(label)] += 1.0

            acc /= sum(acc)

            # predcition probabilities
            max_label = np.argmax(acc)

            if max_label == self.reader.train_data[id].label:
                decisions[i] = True
                scores[i] = acc[max_label]
            else:
                decisions[i] = False

        return decisions, scores

    def compute_decision_for_dataset(self):
        probabilities = np.zeros(self.size_of_data, dtype=float)
        decisions = np.zeros(self.size_of_data, dtype=bool)

        for i in range(self.size_of_data):

            if self.update_counters[i] >= self.queue_size:
                predictions = self.all_predictions[i]
            else:
                predictions = np.zeros(self.update_counters[i], dtype=int)
                for j in range(self.update_counters[i]):
                    predictions[j] = self.all_predictions[i][j]

            if len(predictions) == 0:
                probabilities[i] = 0.0
                decisions[i] = False
            else:
                acc = np.zeros(self.num_of_classes, dtype=float)
                for label in predictions:
                    acc[int(label)] += 1.0
                acc /= sum(acc)

                # decision
                argmax_label = np.argmax(acc)

                if argmax_label == self.reader.train_data[i].label:
                    decisions[i] = True
                else:
                    decisions[i] = False

        return decisions

    def get_trusted_samples(self, reader, ids, images, labels):

        decisions, scores = self.compute_decision_for_batch(ids)
        num_clean_instances = int(np.floor(float(len(ids)) * (1.0 - self.reader.noise_rate)))

        score_threshold = 0
        if sum(decisions) > num_clean_instances:
            #compute thresuold
            sorted_scores = -np.sort(-scores)
            score_threshold = np.fmin(sorted_scores[num_clean_instances], 0.999)

        clean_ids = []
        clean_images = []
        clean_labels = []

        for i in range(len(ids)):
            # introduce threshold for 100 clean. -> plot
            if (len(clean_ids) < num_clean_instances) and (decisions[i] == True) and (scores[i] > score_threshold):
                clean_ids.append(ids[i])
                clean_images.append(images[i])
                clean_labels.append(labels[i])

        # clean hit rate
        if reader.noise_type != "None":
            hit_rate = 0.0
            for ids in clean_ids:
                if reader.train_data[ids].true_label == reader.train_data[ids].label:
                    hit_rate += 1.0

            hit_rate /= float(len(clean_ids))
        else:
            hit_rate = -1.0

        return clean_ids, clean_images, clean_labels, hit_rate

    def save_history(self, path):

        # format: sample id, true_label, noisy label, counter, [predicted labels]
        f = open(path, "w")
        for id in range(len(self.all_predictions)):
            if self.correcter is None:
                f.write(str(id) + ", " + str(self.reader.train_data[id].true_label) + ", " + str(self.reader.train_data[id].label) + ", " + str(self.update_counters[id]) + ", ")
            else:
                # if selfie, we use the corrected labels
                if self.correcter.corrected_labels[id] == -1: # not corrected yet
                    f.write(str(id) + ", " + str(self.reader.train_data[id].label) + ", " + str(self.update_counters[id]) + ", ")
                else:
                    f.write(str(id) + ", " + str(self.correcter.corrected_labels[id]) + ", " + str(self.update_counters[id]) + ", ")
            for j in range(len(self.all_predictions[id])):
                if j != len(self.all_predictions[id]) - 1:
                    f.write(str(self.all_predictions[id][j]) + "|")
                else:
                    f.write(str(self.all_predictions[id][j]) + "\n")
        f.close()
        print(colored("[LOG]", "blue"), "Completed to save history logs in", path)

    def restore(self, path):

        for line in open(path, "r"):
            toks = line.rstrip().split(",")
            id = int(toks[0].strip())
            true_label = int(toks[1].strip())
            noisy_label = int(toks[2].strip())
            counter = int(toks[3].strip())
            predictions_str = toks[4].split("|")

            self.update_counters[id] = counter
            self.reader.train_data[id].label = noisy_label
            for j in range(len(predictions_str)):
                self.all_predictions[id][j] = int(predictions_str[j].strip())
        print(colored("[LOG]", "blue"), "Completed to load history logs from", path)


