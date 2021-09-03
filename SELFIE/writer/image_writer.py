import os, sys,shutil

# Code to write to the file

class image_writer():

    def save_files (dir, samples):
        # dir = "./SELFIE/writer/output/"
        for sample in samples:
            path = dir+str(sample.last_corrected_label)+"/"
            if (os.path.isdir(path)) :
                print ("Output folder: "+str(sample.last_corrected_label)+" already present.")
            else :
                os.makedirs(path,exist_ok=True)
                print("Created output folder: "+str(sample.last_corrected_label))
            shutil.copy(sample.image, path)
            print("Copied file: "+str(sample.label)+" to folder: "+str(sample.last_corrected_label))