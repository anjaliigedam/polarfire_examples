#!/usr/bin/env python
# coding: utf-8

# In[43]:


from tflite_runtime.interpreter import Interpreter 
from PIL import Image
import numpy as np
import time

def load_labels(path): # Read the labels from the text file as a Python list.
    with open(path, 'r') as f:
        return [line.strip() for i, line in enumerate(f.readlines())]

def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
    set_input_tensor(interpreter, image)

    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

    ordered = np.argpartition(-output, 1)
    return [(i, output[i]) for i in ordered[:top_k]][0]

data_folder = "/home/thales/Documents/Quantized_MbnetV2/"

model_path = data_folder + "Mbnet_gear.tflite"
label_path = data_folder + "Labels_Quantized_Mbnetv2_Gear.txt"

interpreter = Interpreter(model_path)
print("Model Loaded Successfully.")


# In[44]:


interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
print("Image Shape (", width, ",", height, ")")


# In[102]:


import cv2

# Load an image to be classified.
#image = cv2.imread(data_folder + "Good_img_70_CLAHE_shp.bmp").resize((width, height))
image = Image.open(data_folder + "Damage_img_6_CLAHE_shp.bmp").convert('RGB').resize((width, height))
input_mean = 0.    
input_std = 255.

input_img = (np.float32(image) - input_mean) / input_std


# In[103]:


# Classify the image.
time1 = time.time()
label_id, prob = classify_image(interpreter, image)
time2 = time.time()
classification_time = np.round(time2-time1, 3)
print("Classification Time =", classification_time, "seconds.")

# Read class labels.
labels = load_labels(label_path)

# Return the classification label of the image.
classification_label = labels[label_id]
print("Image Label is :", classification_label, ", with Accuracy :", np.round(prob*100, 2), "%.")


# In[ ]:




