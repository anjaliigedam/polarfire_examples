# get the ifconfig of ip_camera
ip_camera_url = 'http://192.168.0.107:8080'
ip_camera_url = 'http://192.168.0.110:8080'

import requests
import time
from PIL import Image
from PIL import ImageFont, ImageDraw
import shutil

    
#=============================================================
# get image from ip-camera
#=============================================================
for i in range(1, 6):
    print(f'\nGetting img from ip-camera i = {i}')
    response = requests.get(ip_camera_url)
    
    print(f'response = {response}')

    with open('test.jpg', 'wb') as out_file:
        out_file.write(response.content)
    del response

    print("updated received image to test.jpg")
    print("sleep for 2 seconds")
    time.sleep(2)

    

