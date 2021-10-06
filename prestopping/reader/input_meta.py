# Data Folder Path
CIFAR10_META = {
    "name": "CIFAR-10",
    "path": "/datasets/CIFAR-10", # data path
    "shape": [32, 32, 3], # height, width, depth
    "resize": None,
    "num_train": 49000,
    "num_validation": 1000,
    "num_test": 10000,
    "train_files": ["train_batch_1.bin", "train_batch_2.bin", "train_batch_3.bin", "train_batch_4.bin", "train_batch_5.bin"],
    "validation_files": ["validation_batch.bin"],
    "test_files": ["test_batch.bin"],
    "num_labels": 10
    }

CIFAR100_META = {
    "name": "CIFAR-100",
    "path": "/datasets/CIFAR-100", # data path
    "shape": [32, 32, 3], # height, width, depth
    "resize": None,
    "num_train": 49000,
    "num_validation": 1000,
    "num_test": 10000,
    "train_files": ["train_batch_1.bin", "train_batch_2.bin", "train_batch_3.bin", "train_batch_4.bin", "train_batch_5.bin"],
    "validation_files": ["validation_batch.bin"],
    "test_files": ["test_batch.bin"],
    "num_labels": 100
}

CUSTOM = {
    "name": "custom",
    "path": "/datasets/CIFAR-10", # data path
    "shape": [32, 32, 3], # height, width, depth
    "resize": None,
    "num_train": 1050,
    "num_validation": 1050,
    "num_test": 1050,
    "train_files": ["train_batch_1.bin", "train_batch_2.bin", "train_batch_3.bin", "train_batch_4.bin", "train_batch_5.bin"],
    "validation_files": ["validation_batch.bin"],
    "test_files": ["test_batch.bin"],
    "num_labels": 5
}

SCAN = {
    "name": "scan",
    "path": "/datasets/CIFAR-100", # data path
    "shape": [32, 32, 3], # height, width, depth
    "resize": None,
    "num_train": 610,
    "num_validation": 72,
    "num_test": 315,
    "train_files": ["train_batch_1.bin", "train_batch_2.bin", "train_batch_3.bin", "train_batch_4.bin", "train_batch_5.bin"],
    "validation_files": ["validation_batch.bin"],
    "test_files": ["test_batch.bin"],
    "num_labels": 4
}
