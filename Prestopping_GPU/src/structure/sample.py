class Sample(object):
    def __init__(self, id, image, true_label):
        # image id
        self.id = id
        # image pixels
        self.image = image
        # image true label
        self.true_label = true_label
        # image corrupted label
        self.label = true_label
        # sample type: [0: true-labeled, 1: false-labeled]
        self.type = 0

    def toString(self):
        return "Id: " + str(self.id) + ", Label: ", + str(self.label)
