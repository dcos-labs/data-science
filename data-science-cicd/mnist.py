# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


#!/usr/bin/env python2.7
r"""Train and export a simple Softmax Regression TensorFlow model.
The model is from the TensorFlow "MNIST For ML Beginner" tutorial. This program
simply follows all its training instructions, and uses TensorFlow SavedModel to
export the trained model with proper signatures that can be loaded by standard
tensorflow_model_server.
Usage: mnist_saved_model.py [--training_iteration=x] [--model_version=y] \
    export_dir
"""

from __future__ import print_function

import os
import sys

# This is a placeholder for a Google-internal import.

import tensorflow as tf

from tensorflow.examples.tutorials.mnist import input_data


def train(server, log_dir, context):

  fake_data = context.get('fake_data') or False
  training_iteration = context.get('max_steps') or 100
  learning_rate = context.get('learning_rate') or 0.001
  dropout = context.get('dropout') or 0.9
  work_dir = context.get('work_dir') or '/tmp'
  run_name = context.get('run_name') or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
  export_path_base = context.get('export_path_base') or '/tmp'
  model_version = context.get('model_version') or '0'



  # Train model
  # Create a multilayer model.
  with tf.device(tf.train.replica_device_setter(
            worker_device="/job:worker/task:%d" %
                          server.server_def.task_index,
            cluster=server.server_def.cluster)):

    print('Training model...')
    mnist = input_data.read_data_sets(work_dir, one_hot=True)
    # sess = tf.InteractiveSession()
    serialized_tf_example = tf.placeholder(tf.string, name='tf_example')
    feature_configs = {'x': tf.FixedLenFeature(shape=[784], dtype=tf.float32),}
    tf_example = tf.parse_example(serialized_tf_example, feature_configs)
    x = tf.identity(tf_example['x'], name='x')  # use tf.identity() to assign name
    y_ = tf.placeholder('float', shape=[None, 10])
    w = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))


    is_chief = server.server_def.task_index == 0
    hooks=[tf.train.StopAtStepHook(last_step=training_iteration)]


    #with tf.train.MonitoredTrainingSession(master=server.target,
    #                                       is_chief=is_chief,
    #                                       hooks=hooks) as sess:
    with tf.Session(server.target) as sess:

      sess.run(tf.global_variables_initializer())
      y = tf.nn.softmax(tf.matmul(x, w) + b, name='y')
      cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
      train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)
      values, indices = tf.nn.top_k(y, 10)
      table = tf.contrib.lookup.index_to_string_table_from_tensor(
          tf.constant([str(i) for i in xrange(10)]))
      prediction_classes = table.lookup(tf.to_int64(indices))
      for _ in range(training_iteration):
        batch = mnist.train.next_batch(50)
        train_step.run(feed_dict={x: batch[0], y_: batch[1]})
      correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
      accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
      print('training accuracy %g' % sess.run(
          accuracy, feed_dict={
              x: mnist.test.images,
              y_: mnist.test.labels
          }))
      print('Done training!')


      if is_chief:
        # Export model
        # WARNING(break-tutorial-inline-code): The following code snippet is
        # in-lined in tutorials, please update tutorial documents accordingly
        # whenever code changes.
        export_path = os.path.join(
            tf.compat.as_bytes(export_path_base),
            tf.compat.as_bytes(str(model_version)))
        print('Exporting trained model to', export_path)
        builder = tf.saved_model.builder.SavedModelBuilder(export_path)

        # Build the signature_def_map.
        classification_inputs = tf.saved_model.utils.build_tensor_info(
            serialized_tf_example)
        classification_outputs_classes = tf.saved_model.utils.build_tensor_info(
            prediction_classes)
        classification_outputs_scores = tf.saved_model.utils.build_tensor_info(values)

        classification_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs={
                    tf.saved_model.signature_constants.CLASSIFY_INPUTS:
                        classification_inputs
                },
                outputs={
                    tf.saved_model.signature_constants.CLASSIFY_OUTPUT_CLASSES:
                        classification_outputs_classes,
                    tf.saved_model.signature_constants.CLASSIFY_OUTPUT_SCORES:
                        classification_outputs_scores
                },
                method_name=tf.saved_model.signature_constants.CLASSIFY_METHOD_NAME))

        tensor_info_x = tf.saved_model.utils.build_tensor_info(x)
        tensor_info_y = tf.saved_model.utils.build_tensor_info(y)

        prediction_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs={'images': tensor_info_x},
                outputs={'scores': tensor_info_y},
                method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

        legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
        builder.add_meta_graph_and_variables(
            sess, [tf.saved_model.tag_constants.SERVING],
            signature_def_map={
                'predict_images':
                    prediction_signature,
                tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                    classification_signature,
            },
            legacy_init_op=legacy_init_op)

        builder.save()

        print('Done exporting!')


def main(server, log_dir, context):
    """
    server: a tf.train.Server object (which knows about every other member of the cluster)
    log_dir: a string providing the recommended location for training logs, summaries, and checkpoints
    context: an optional dictionary of parameters (batch_size, learning_rate, etc.) specified at run-time
    """
    train(server, log_dir, context)
