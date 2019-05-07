#!/usr/bin/env python
# coding: utf-8

# # Save model for Tensorflow Serving
# ## Lifted mostly from https://www.tensorflow.org/tfx/serving/tutorials/Serving_REST_simple

# In[ ]:


# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
# s3 model storage
import boto3
from botocore.client import Config
# Helper libraries
import numpy as np
import json
import matplotlib.pyplot as plt
import os
import subprocess
import time

print(tf.__version__)


# In[ ]:


fashion_mnist = keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

# scale the values to 0.0 to 1.0
train_images = train_images / 255.0
test_images = test_images / 255.0

# reshape for feeding into the model
train_images = train_images.reshape(train_images.shape[0], 28, 28, 1)
test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

print('\ntrain_images.shape: {}, of {}'.format(train_images.shape, train_images.dtype))
print('test_images.shape: {}, of {}'.format(test_images.shape, test_images.dtype))


# In[ ]:


model = keras.Sequential([
  keras.layers.Conv2D(input_shape=(28,28,1), filters=8, kernel_size=3, 
                      strides=2, activation='relu', name='Conv1'),
  keras.layers.Flatten(),
  keras.layers.Dense(10, activation=tf.nn.softmax, name='Softmax')
])
model.summary()

testing = False
epochs = 5

model.compile(optimizer=tf.train.AdamOptimizer(), 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(train_images, train_labels, epochs=epochs)

test_loss, test_acc = model.evaluate(test_images, test_labels)
print('\nTest accuracy: {}'.format(test_acc))


# In[ ]:


# Fetch the Keras session and save the model
# The signature definition is defined by the input and output tensors,
# and stored with the default serving key
import tempfile

MODEL_NAME = 'mnist'
MODEL_DIR = tempfile.gettempdir() + '/' + MODEL_NAME
MODEL_VERSION = str(int(time.time()))
export_path = os.path.join(MODEL_DIR, str(MODEL_VERSION))
print('export_path = {}\n'.format(export_path))
if os.path.isdir(export_path):
  print('\nAlready saved a model, cleaning up\n')
  get_ipython().system('rm -r {export_path}')

tf.saved_model.simple_save(
    keras.backend.get_session(),
    export_path,
    inputs={'input_image': model.input},
    outputs={t.name:t for t in model.outputs})


# ## Test
# View image

# In[ ]:


pic = test_images[0:1]
plt.imshow(pic.reshape(28,28))


# Save image as image.json

# In[ ]:


data = json.dumps({"signature_name": "serving_default", "instances": pic.tolist()})
with open('image.json', 'w') as f:
  f.write(data)


# Move model to serving directory, then check<br>
# curl -X POST -H "Content-Type: application/json" -d @image.json http://loadbalancerIP:assginedPORT/v1/models/mnist:predict
# <br>Result:<br>
# {
#     "predictions": [[1.65433e-06, 1.64561e-07, 3.53323e-06, 2.86745e-06, 6.96201e-06, 0.0273952, 2.95962e-05, 0.157299, 0.00583552, 0.809425]
#     ]
# }
# <br> Therefore, the last element is most likely (Ankle boot).

# ### Can use s3 to store models
# ```
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# s3 = boto3.resource('s3',
#                     endpoint_url='http://minio.marathon.l4lb.thisdcos.directory:9000',
#                     aws_access_key_id=AWS_ACCESS_KEY_ID,
#                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                     config=Config(signature_version='s3v4'),
#                     region_name='us-east-1')
# 
# MODEL_WRITE = MODEL_NAME + '/' + MODEL_VERSION + '/saved_model.pb'
# MODEL_READ = '/tmp/' + MODEL_WRITE
# 
# s3.Bucket('models').upload_file(MODEL_READ,MODEL_WRITE)
# MODEL_WRITE
# ```
