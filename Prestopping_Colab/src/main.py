import sys, os
from reader import input_meta
from pathlib import Path
from phase.entire_methods import *
from algorithm.run_compared_method import *

def main():
    print("------------------------------------------------------------")
    print("This code supports All robust training methods in our paper.")
    print("**Description**")
    print("All algorithm parameters are set to the default values in our papers.")
    print("For training, training_epoch = 120, batch_size = 128, initial_learning_rate = 0.1 (decayed at 50% and 75% of total number of epochs), See the paper for the detailed experimental configuration.")

    if len(sys.argv) != 8:
        print("Run Cmd: python main.py [gpu_id] [data_name] [model_name] [method_name] [noise_type] [noise_rate] [log_dir]")
        print("**Parameters**")
        print("1. gpu_id: gpu number which you want to use.")
        print("2. data_name: {CIFAR-10, CIFAR-100}")
        print("3. model_name: {DenseNet-10-12, DenseNet-25-12, DenseNet-40-12, VGG-19}")
        print("4. method_name: {Default, ActiveBias, Coteaching, CoteachingPlus, SELFIE, Prestopping, PrestoppingPlus}")
        print("5. noise_type: {Pair, Symmetric, None}")
        print("6. noise_rate: the rate which you want to corrupt, E.g., 0.4")
        print("7. log_dir: log directory to save training loss/acc and test loss/acc")
        sys.exit()

    # for user parameter: [gpu_id] [data_name] [model_name] [method_name] [noise_type] [noise_rate] [log_dir]
    gpu_id = int(sys.argv[1])
    data_name = sys.argv[2]
    model_name = sys.argv[3]
    method_name = sys.argv[4]
    noise_type = sys.argv[5]
    noise_rate = float(sys.argv[6])
    log_dir = sys.argv[7]

    # Get root path of this source code
    data_path_root = str(Path(os.path.dirname((os.path.abspath(__file__)))).parent) + "/datasets/"
    print("[Src path]: ", data_path_root)
    if os.path.exists(data_path_root):
        print("Dataset exists in", data_path_root)
        # change "input_meta" files for the data root path.
        if data_name == "CIFAR-10":
            input_meta.CIFAR10_META["path"] = data_path_root + data_name
        elif data_name == "CIFAR-100":
            input_meta.CIFAR100_META["path"] = data_path_root + data_name
        else:
            print("This is sample code for synthetic noise. I will update this integrated source code for the real-world data soon.")
            sys.exit(1)
    else:
        print("Dataset doesn't exist in", data_path_root, ", please download and locate them in that folder.")
        sys.exit(1)

    # Default training configuration
    # total_epoch = 120
    total_epoch = 4
    batch_size = 128
    lr_values = [0.1, 0.02, 0.004]
    lr_boundaries = [60, 90]
    optimizer = "momentum"

    if method_name in ["Default", "ActiveBias", "Coteaching", "CoteachingPlus", "SELFIE"]:
        approach = ComparedMethodRunner(gpu_id, data_name, model_name, method_name, noise_type=noise_type, noise_rate=noise_rate, log_dir=log_dir)
        approach.run(total_epoch=total_epoch, batch_size=batch_size, lr_values=lr_values, lr_boundaries=lr_boundaries, optimizer=optimizer)
    elif method_name in ["Prestopping", "PrestoppingPlus"]:
        approach = TwoPhaseMethod(gpu_id, data_name, model_name, method_name, noise_type=noise_type, noise_rate=noise_rate, log_dir=log_dir)
        approach.run_all_phases(total_epoch=total_epoch, batch_size=batch_size, lr_values=lr_values, lr_boundaries=lr_boundaries, optimizer=optimizer, warm_up_epoch=25)
    else:
        print("Use the method in {Default, ActiveBias, Coteaching, CoteachingPlus, SELFIE, Prestopping, PrestoppingPlus}")

if __name__ == '__main__':
    print(sys.argv)
    main()