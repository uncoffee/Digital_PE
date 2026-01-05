#pip要る
import pygame 
import cv2 #pip install opencv-python モジュ:pip install opencv-contrib-python
import hid #pip install hidapi
import math

#pipいらない
import numpy
import random
import sys
import time


def random_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

def image_changer(img_name,size):
    img = pygame.image.load(img_name)
    scale = size / img.get_width()
    img_data = pygame.transform.scale(img, (img.get_width()*scale, img.get_height()*scale))
    return img_data

class random_choice:
    def __init__(self , display_info , setting):
        self.display_info = display_info #辞書型で来ているので注意。
        self.Setting = setting #辞書型で来ているので注意。
        self.choice_log = {"entity" : None ,"width" : None , "height" : None}
        
    def choice(self , entity_list):
        if type(entity_list) == list:
            return None
        
        while not self.choice_log["entity"] == entity:
            entity = random.choice(entity_list)
        self.choice_log["entity"] = entity

        if entity.info["random_choice"] == True:
            while not np.abs(self.choice_log["width"] - self.display_info["width"]) < self.setting["frame_size"]:
                entity.draw_point["width"] = random.randint(self.display_info["width"])
            self.choice_log["width"] = entity.draw_point["width"]
        
            while not np.abs(self.choice_log["height"] - self.display_info["height"]) < self.setting["frame_size"]:
                entity.draw_point["height"] = random.randint(self.display_info["height"])
            self.choice_log["height"] = entity.draw_point["height"]