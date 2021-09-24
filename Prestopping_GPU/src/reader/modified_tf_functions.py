from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from termcolor import colored
from tensorflow.python.eager import context
from tensorflow.python.framework import ops
from tensorflow.python.ops import data_flow_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.summary import summary
from tensorflow.python.training import input as tf_input

def generate_image_and_label_batch(s_id, s_image, s_label, batch_size, num_images, min_fraction_of_examples_in_queue, num_preprocess_threads, shuffle=False):
    # Ensure that the random shuffling has good mixing properties.
    min_queue_examples = int(num_images * min_fraction_of_examples_in_queue)
    #print( colored("[LOG]", "blue"), "Filling queue with %d data before starting to train. This will take a few minutes." % min_queue_examples)
    t_id, t_images, t_label = shuffle_batch([s_id, s_image, s_label], batch_size=batch_size,
                                            num_threads=num_preprocess_threads,
                                            capacity=min_queue_examples + 3 * batch_size,
                                            min_after_dequeue=min_queue_examples,
                                            shuffle=shuffle)
    return t_id, t_images, t_label

def shuffle_batch(tensors, batch_size, capacity, min_after_dequeue,
                  num_threads=1, seed=None, enqueue_many=False, shapes=None,
                  allow_smaller_final_batch=False, shared_name=None, name=None, shuffle=True):
    return _custom_shuffle_batch(
        tensors,
        batch_size,
        capacity,
        min_after_dequeue,
        keep_input=True,
        num_threads=num_threads,
        seed=seed,
        enqueue_many=enqueue_many,
        shapes=shapes,
        allow_smaller_final_batch=allow_smaller_final_batch,
        shared_name=shared_name,
        name=name,
        shuffle=shuffle)

# Modified Tensorflow API for FIFO queue, instead of SHUFFLE Queue
def _custom_shuffle_batch(tensors, batch_size, capacity, min_after_dequeue,
                          keep_input, num_threads=1, seed=None, enqueue_many=False,
                          shapes=None, allow_smaller_final_batch=False,
                          shared_name=None, name=None, shuffle=False):
    """Helper function for `shuffle_batch` and `maybe_shuffle_batch`."""

    if context.executing_eagerly():
        raise ValueError(
            "Input pipelines based on Queues are not supported when eager execution"
            " is enabled. Please use tf.data to ingest data into your model"
            " instead.")
    tensor_list = tf_input._as_tensor_list(tensors)
    with ops.name_scope(name, "shuffle_batch",
                        list(tensor_list) + [keep_input]) as name:
        if capacity <= min_after_dequeue:
            raise ValueError("capacity %d must be bigger than min_after_dequeue %d."
                             % (capacity, min_after_dequeue))
        tensor_list = tf_input._validate(tensor_list)
        keep_input = tf_input._validate_keep_input(keep_input, enqueue_many)
        tensor_list, sparse_info = tf_input._store_sparse_tensors(
            tensor_list, enqueue_many, keep_input)
        types = tf_input._dtypes([tensor_list])
        shapes = tf_input._shapes([tensor_list], shapes, enqueue_many)

        ###########################################################################################
        if shuffle:
            queue = data_flow_ops.RandomShuffleQueue(
                capacity=capacity, min_after_dequeue=min_after_dequeue, seed=seed,
                dtypes=types, shapes=shapes, shared_name=shared_name)
        else:
            # Remove shuffle property
            queue = data_flow_ops.FIFOQueue(capacity=capacity, dtypes=types, shapes=shapes, shared_name=shared_name)
        ###########################################################################################

        tf_input._enqueue(queue, tensor_list, num_threads, enqueue_many, keep_input)
        full = (math_ops.to_float(
            math_ops.maximum(0, queue.size() - min_after_dequeue)) *
                (1. / (capacity - min_after_dequeue)))

        summary_name = (
                "fraction_over_%d_of_%d_full" %
                (min_after_dequeue, capacity - min_after_dequeue))
        summary.scalar(summary_name, full)

        if allow_smaller_final_batch:
            dequeued = queue.dequeue_up_to(batch_size, name=name)
        else:
            dequeued = queue.dequeue_many(batch_size, name=name)

        dequeued = tf_input._restore_sparse_tensors(dequeued, sparse_info)

        return tf_input._as_original_type(tensors, dequeued)
