from image_writer import image_writer

# # Pseduo code
# Sample object
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

        ## for logging ###
        self.last_corrected_label = None
        self.corrected = False

    def toString(self):
        return "Id: " + str(self.id) + ", True Label: ", + str(self.true_label) + ", Corrupted Label: " + str(self.label)

# samples initialization
samples = []
s = Sample (1, "./SELFIE/writer/input/Image1.jpeg","Image1")
samples.append(s)
s = Sample (2, "./SELFIE/writer/input/Image2.jpeg","Image2")
samples.append(s)
s = Sample (3, "./SELFIE/writer/input/Image3.jpeg","Image3")
samples.append(s)
s = Sample (4, "./SELFIE/writer/input/Image4.jpeg","Image1")
samples.append(s)
s = Sample (5, "./SELFIE/writer/input/Image5.jpeg","Image1")
samples.append(s)
s = Sample (6, "./SELFIE/writer/input/Image6.jpeg","Image1")
samples.append(s)
s = Sample (7, "./SELFIE/writer/input/Image7.jpeg","Image1")
samples.append(s)
s = Sample (8, "./SELFIE/writer/input/Image8.jpeg","Image1")
samples.append(s)

# Assuming label correction
samples[0].last_corrected_label="CAT"
samples[1].last_corrected_label="CAT"
samples[2].last_corrected_label="DOG"
samples[3].last_corrected_label="CAT"
samples[4].last_corrected_label="CAT"
samples[5].last_corrected_label="DOG"
samples[6].last_corrected_label="DOG"
samples[7].last_corrected_label="DOG"

outputDir = "./SELFIE/writer/output/"

image_writer.save_files(outputDir,samples)