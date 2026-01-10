"""Copyright (C) 2026 [uncoffee]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


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
    
class print_check():
    def __init__(self):
        self.count = 0

    def c(self):
        self.count += 1
        print(self.count)

class random_choice:
    def __init__(self , random_point=None):
        self.random_point = random_point #辞書型で来ているので注意。
        self.new_choice = {"entity":None,"width":0,"hegint":0}
        if not random_point == None:
            self.choice_log = {"entity" : None ,"width" : random_point["width"]//2 , "height" : random_point["height"] // 2}#二で割ることで中心近くに出現するところから始まる。
        
    def choice(self , entity_list):
        while True:
            self.new_choice["entity"] = random.choice(entity_list)
            if self.random_point == None:
                break

            if not self.choice_log["entity"] == self.new_choice["entity"]:
                self.choice_log["entity"] = self.new_choice["entity"]
                self.new_choice["entity"].choice = True
                break

        if self.random_point == None:
            return
        
        width_max = self.random_point["width"] - self.random_point["padding"]
        width_min = 0 + self.random_point["padding"]
        height_max = self.random_point["height"] - self.random_point["padding"]
        height_min = 0 + self.random_point["padding"]

        while True:
            self.new_choice["width"] = random.randint(width_min ,  width_max)
            if np.abs(self.choice_log["width"] - self.random_point["width"]) > self.random_point["near"]:
                break
        self.choice_log["width"] = self.new_choice["width"]
    
        while True:
            self.new_choice["height"] = random.randint(height_min , height_max)
            if np.abs(self.choice_log["height"] - self.random_point["height"]) > self.random_point["near"]:
                break
        self.choice_log["height"] = self.new_choice["height"]

        self.new_choice["entity"].draw_point = (self.new_choice["width"] , self.new_choice["height"])