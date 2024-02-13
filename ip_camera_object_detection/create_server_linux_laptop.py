
#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""

#!/usr/bin/env python3
## pip install pygame
## select python interpretos /usr/bin/python3

import pygame.camera
from pygame.locals import *
import sys
img_path = "/home/rt/Downloads/server/test.jpg"
SERVER_ADDR = "0.0.0.0"
PORT_NUM = 8080

def get_image():
    pygame.init()
    pygame.camera.init()
    
    cam = pygame.camera.Camera("/dev/video0",(640,480))
    cam.start()
    
    WIDTH = 640
    HEIGHT = 480 
    
    screen = pygame.display.set_mode( ( WIDTH, HEIGHT ) )
    pygame.display.set_caption("Camera View")
    
    image = cam.get_image() 
    screen.blit(image, (0,0))
    pygame.display.flip()
    
    pygame.image.save(image, img_path)
    cam.stop()

#==================

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import time 
from datetime import datetime
import shutil

#SERVER_ADDR = "0.0.0.0"
#PORT_NUM = 8080
my_path = "/home/rt/Downloads/server"
IMAGE_EXTENSION = ".bmp"
IMAGE_NAME_MAX_SIZE = 100


class S(BaseHTTPRequestHandler):
    received_file_name = ""
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        
        get_image()
        #self._set_response()
        #self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
        with open(img_path, 'rb') as content:
            shutil.copyfileobj(content, self.wfile)    

    def do_POST(self):
        global received_file_name
        print("=========do_POST start=======")
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        print(str(self.headers))
        

        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        
        logging.info("POST request %s %s ", str(my_path), str(self.headers))

        self._set_response()
        self.wfile.write("POST request for {}".format(my_path).encode('utf-8'))
        
        if(content_length < IMAGE_NAME_MAX_SIZE):
            received_file_name = post_data.decode() 
            received_file_name = received_file_name.replace(".bmp","")
            print("---------- received_file_name = " + str(received_file_name) + " --------------")
        else:
            file_time = datetime.now().strftime("_%Y_%m_%d-%I_%M_%S_%p")
            file_name = my_path + "/" + received_file_name + file_time + IMAGE_EXTENSION
            file = open(file_name, 'wb') 
            pos = post_data.find(b"\r\n\r\n")
            
            post_data = post_data[pos+4:]
            file.write(post_data)

            file.close() 
            print("----------file recevied and written : " + str(file_name) + " ------------")
        print("=========do_POST done=======\n\n")


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = (SERVER_ADDR, PORT_NUM)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    print(server_address)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
