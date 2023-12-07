# Model_path, Label_path and Image_path are user-defined
# Min_conf_threshold on line 28 can be tuned between 0.5 to 0.95 in steps of 0.05. The lower the threshold, the higher the detections, but at a risk of increased false positives
# This script is for running inference on a single image 


Model_path = "/home/root/thales/Documents/CMTI_TFLite_OD_model/Defect_detect.tflite"
Label_path = "/home/root/thales/Documents/CMTI_TFLite_OD_model/label_map.txt"
Image_path = "/home/root/thales/Documents/CMTI_TFLite_OD_model/Image_data/Good_img_48_CLAHE_shp.bmp"

from tflite_runtime.interpreter import Interpreter
from PIL import Image
import numpy as np
import time

print("debug 1")
interpreter = Interpreter(Model_path)
print("debug 2")

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
_, height, width, _ = input_details[0]['shape']
print("Image Shape (", width, ",", height, ")")

print("debug 3")

interpreter.allocate_tensors()

print("debug 4")

with open(Label_path,'r') as text:
    labels = [line.strip() for line in text.readlines()]

min_conf_threshold = 0.55

img = Image.open(Image_path)
resized_img = img.resize((width, height))
input_mean = 127.5
input_std = 127.5
norm_img = (np.float32(resized_img) - input_mean)/input_std
img_tensor = np.expand_dims(norm_img, axis=0)
start_time = time.time()
interpreter.set_tensor(input_details[0]['index'],img_tensor)
interpreter.invoke()
  
scores = interpreter.get_tensor(output_details[0]['index']) # Probabilities/ scores of detected objects
boxes = interpreter.get_tensor(output_details[1]['index']) # Bounding box coordinates (normalized [0,1]) of detected objects
count = interpreter.get_tensor(output_details[2]['index']) # Number of detected objects
classes = interpreter.get_tensor(output_details[3]['index']) # Class indices/ labels of detected objects

results = []
for i in range(int(count[0])):
    if scores[0, i] > min_conf_threshold:
        result = {
                'bounding_box': boxes[0, i],
                'class_id': labels[int(classes[0, i])],
                'score': '%d%%' % (int(scores[0, i]*100))
        }
        results.append(result)

end_time = time.time()
detection_time = np.round(end_time - start_time, 3)

print(results)  #This should print a list of dictionaries comprising the bounding box coordinates, class_id and score for each detection      
print("Detection time:", detection_time, "seconds")

