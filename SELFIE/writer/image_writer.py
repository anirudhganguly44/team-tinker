import os, sys,shutil

# Code to write to the file

class image_writer():

    def save_files (dir, samples):
        # dir = "./SELFIE/writer/output/"
        print("Total samples: ", len(samples))
        for sample in samples:
            path = dir+str(sample.true_label)
            # print("PATH: "+path)
            if (os.path.isdir(path)):
                print ("Output folder: "+str(sample.true_label)+" already present.")
            else:
                os.makedirs(path,exist_ok=True)
                print("Created output folder: "+str(sample.true_label))
            
            if sample.image is None:
                print("Image not present!")
            else:
                # print (str(sample.true_label))
                try:
                    shutil.copy(sample.image, str(path+'.jpg'))
                    print("Copied file: "+str(sample.label)+" to folder: "+str(sample.true_label))
                    # print("File copied successfully.")
                
                # If source and destination are same
                except shutil.SameFileError:
                    print("Source and destination represents the same file.")
                
                # If there is any permission issue
                except PermissionError:
                    print("Permission denied.")
                
                # For other errors
                except:
                    e = str(sys.exc_info())
                    print("Error occurred while copying file.\n"+ e)
                    break
                