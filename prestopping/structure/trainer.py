
class Trainer(object):
    def __init__(self, model):
        self.model = model
        self.train_loss_op = None
        self.train_accuracy_op = None
        self.train_op = None
        self.train_xentropy_op = None
        self.train_prob_op = None
        self.test_loss_op = None
        self.test_accuracy_op = None
        self.test_xentropy_op = None
        self.test_prob_op = None