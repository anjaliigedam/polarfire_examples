# Model_path, Label_path and Image_path are user-defined
# Min_conf_threshold on line 28 can be tuned between 0.5 to 0.95 in steps of 0.05. The lower the threshold, the higher the detections, but at a risk of increased false positives
# This script is for running inference on a single image 

USE_FLOAT = 0
print("USE_FLOAT =" +str(USE_FLOAT))
if(USE_FLOAT == 1):
    Model_path = "Defect_detect.tflite" #float
else:
    Model_path = "CMTI_gear_detect.tflite" #uint8

Label_path = "label_map.txt"
image_path = "test_images"
output_path = "output_images"

# ontime create the server on Linux laptop
# >> python3 create_server_linux_laptop.py
# ADDR = 127.0.0.1 PORT = 8808
server_url = 'http://0.0.0.0:8080'

import requests
from tflite_runtime.interpreter import Interpreter
from PIL import Image
import numpy as np
import time
import pprint
from PIL import ImageFont, ImageDraw



interpreter = Interpreter(Model_path)

import glob
arr_img = glob.glob(image_path + "/*.bmp")
length = len(arr_img)
print("array_images =" +str(arr_img))

for test_img in range(length):

    print("Input Image =", arr_img[test_img])

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    _, height, width, _ = input_details[0]['shape']
    print("Image Shape (", width, ",", height, ")")

    interpreter.allocate_tensors()

    with open(Label_path,'r') as text:
        labels = [line.strip() for line in text.readlines()]

    min_conf_threshold = 0.55

    img = Image.open(arr_img[test_img])
    resized_img = img.resize((width, height))
    
    if(USE_FLOAT == 1):
        input_mean = 127.5
        input_std = 127.5
        norm_img = (np.float32(resized_img) - input_mean)/input_std
        img_tensor = np.expand_dims(norm_img, axis=0)
    else:
        img_tensor = np.expand_dims(resized_img, axis=0)

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
    pprint.pprint(results)
    print("Detection time:", detection_time, "seconds")
    print('\n')

    #=============================================================
    # generate image
    #=============================================================
    
    # Open image and get image dimensions
    img = Image.open(arr_img[test_img])
    imW, imH = img.size
    draw = ImageDraw.Draw(img)

    for d in results:
        xmin = int(max(1,(d['bounding_box'][1] * imW)))
        ymin = int(max(1,(d['bounding_box'][0] * imH)))
        xmax = int(min(imW,(d['bounding_box'][3] * imW)))
        ymax = int(min(imH,(d['bounding_box'][2] * imH)))
        txt = " {}: {}".format(d['class_id'], d['score'])
        font = ImageFont.truetype("LiberationMono-Regular.ttf", 14)
        #font = ImageFont.load_default()
        ts = draw.textlength(txt, font=font)
        draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=4)
        draw.text((xmin-8, ymin-8), txt, font=font, fill="white", stroke_width=2, stroke_fill="black")

    img_name = arr_img[test_img]
    img_name = img_name.replace(image_path,"").strip("/")
    out_img = output_path + "/" + img_name
    print("Dumping out_img = " + out_img)
    img.save(out_img)


    
    #=============================================================
    # push image on server
    #=============================================================
    print("Pushing out_img onto Server")
    getdata = requests.post(server_url, data=img_name)

    #files = {'file': open(image_name, 'rb')}
    files = {'fieldname': (out_img, open(out_img,'rb').read())}
    getdata = requests.post(server_url, files=files)
    
