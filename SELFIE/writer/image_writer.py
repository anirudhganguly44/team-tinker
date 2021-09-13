import os, sys,shutil
from matplotlib import pyplot
import cv2
import numpy as np

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
                # pyplot.imshow(sample.image)
                # pyplot.imsave(filename,sample.image)
                #img = cv2.cvtColor(sample.image, cv2.COLOR_GRAY2BGR)

                #Sharpen the image
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                img = cv2.convertScaleAbs(sample.image, alpha=(255.0))
                im = cv2.filter2D(img, -1, kernel)
                
                # resize image
                scale_percent = 500 # percent of original size
                width = int(im.shape[1] * scale_percent / 100)
                height = int(im.shape[0] * scale_percent / 100)
                dim = (width, height)
  
                resized = cv2.resize(im, dim, interpolation = cv2.INTER_AREA)
 
                #print('Resized Dimensions : ',resized.shape)
 
                #re_img = cv2.imshow("Resized image", resized)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                cv2.imwrite(filename,resized)
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
                