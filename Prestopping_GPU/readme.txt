###############################################################
###### You can download our source codes and data sets ########
###### in anonymized dropbox: https://bit.ly/2l3g9Jx   ########
###############################################################

1. Requirement
 - python3 (we used 3.6.4)
 - tensorflow-gpu (we used 1.8.0)
 - tensorpack libracy //use "pip install tensorpack"
 
 2. Description
 - Source code covers all methods compared in our paper.
 - Algorithm paramters were set to be the same as in our paper.
 - *** Required User Parameters ***
	1. gpu_id: gpu number which you want to use.
	2. data_name: {CIFAR-10, CIFAR-100}
	3. model_name: {DenseNet-10-12, DenseNet-25-12, DenseNet-40-12, VGG-19}
	4. method_name: {Default, ActiveBias, Coteaching, CoteachingPlus, SELFIE, Prestopping, PrestoppingPlus}
	5. noise_type: {Pair, Symmetric, None}
	6. noise_rate: the rate which you want to corrupt, E.g., 0.4
	7. log_dir: log directory to save training loss/acc and test loss/acc

 3. Data Set
 - Data sets are located in "datasets" folder
 - Please download the "src" and "datasets" folder and locate them in the same folder.
 
 4. *** Running Command in "main.py" ***
 - python main.py [gpu_id] [data_name] [model_name] [method_name] [noise_type] [noise_rate] [log_dir]
 - E.g., python main.py 0 CIFAR-100 DenseNet-40-12 Prestopping Pair 0.4 log_pair_0.4/Prestopping

 5. Format of log file
 - Basically, all log files include training loss/error, validation loss/error, test loss/error
 - E.g., "Convergence_log.csv": num_epoch, learning_rate, training loss, training error, validation loss, validation error, test loss, test error
 - See the details in the source code