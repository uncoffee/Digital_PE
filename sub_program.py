#pip要る
import pygame 
import cv2 #pip install opencv-python モジュ:pip install opencv-contrib-python
import hid #pip install hidapi
import math

#pipいらない
import numpy as np
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

class draw_text:
    def __init__(self,info):
        self.draw_point = info["draw_point"]
        self.pallet = info["pallet"]
        self.font = info["font"]
        self.color = info["color"]
        self.Anti_Aliasing = info["Anti_Aliasing"]

    def draw(self,text):
        text_surface = self.font.render(text, self.Anti_Aliasing, self.color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.draw_point)

        self.pallet.blit(text_surface , text_rect)

    def get_data(self,text):
        text_surface = self.font.render(text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.draw_point)

        return (text_surface , text_rect)
    
class random_choice:
    def __init__(self , random_point=None):
        self.random_point = random_point #辞書型で来ているので注意。
        self.choice_log = {"entity" : None ,"width" : None , "height" : None}
        
    def choice(self , entity_list):
        
        while True:
            entity = random.choice(entity_list)
            if not self.choice_log["entity"] == entity:
                break

        self.choice_log["entity"] = entity

        if not self.random_point == None:
            while True:
                entity.draw_point["width"] = random.randint(self.random_point["width"])
                if np.abs(self.choice_log["width"] - self.random_point["width"]) > self.random_point["padding"]:
                    break
            self.choice_log["width"] = entity.draw_point["width"]
        
            while True:
                entity.draw_point["height"] = random.randint(self.random_point["height"])
                if np.abs(self.choice_log["height"] - self.random_point["height"]) > self.random_point["padding"]:
                    break
            self.choice_log["height"] = entity.draw_point["height"]