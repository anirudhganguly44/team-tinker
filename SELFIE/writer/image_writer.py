import os, sys,shutil
from matplotlib import pyplot
import cv2

# Code to write to the file

class image_writer():

    def save_files (dir, samples):
        # dir = "./SELFIE/writer/output/"
        print("Total samples: ", len(samples))
        for sample in samples:
            path = dir+str(sample.last_corrected_label)+"/"
            # print("PATH: "+path)
            if not (os.path.isdir(path)):
                os.makedirs(path,exist_ok=True)
                #print ("Output folder: "+str(sample.last_corrected_label)+" already present.")
            #else:
               # os.makedirs(path,exist_ok=True)
                #print("Created output folder: "+str(sample.last_corrected_label))
            
            if sample.image is None:
                print("Image not present!")
            else:
                filename = path+str(sample.true_label)+".png"
                pyplot.imshow(sample.image)
                pyplot.imsave(filename,sample.image)
                #cv2.imwrite(filename,sample.image)
                # try:
                #     shutil.copy(sample.image, str(path+'.jpg'))
                #     print("Copied file: "+str(sample.last_corrected_label)+" to folder: "+str(path))
                #     # print("File copied successfully.")
                
                # # If source and destination are same
                # except shutil.SameFileError:
                #     print("Source and destination represents the same file.")
                
                # # If there is any permission issue
                # except PermissionError:
                #     print("Permission denied.")
                
                # # For other errors
                # except:
                #     e = str(sys.exc_info())
                #     print("Error occurred while copying file.\n"+ e)
                #     break
                