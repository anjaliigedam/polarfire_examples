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











#
#
#
## laptop 
## when post is received with data = send
## send a post
#
#
## kit
## send post
## handle post(to take data)


