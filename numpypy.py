import pygame 
import cv2 #pip install opencv-python モジュ:pip install opencv-contrib-python
import hid #pip install hidapi
import math

#pipいらない
import numpy
import random
import sys
import time

# img_size = int(input("画像の大きさを半角で入力 : "))

# magnification = img_size / 180
# print(f"xのズレ:{-90 * magnification} , yのズレ{-50 * magnification}")

# screen_width = 1920
# screen_height = 1080

# print(((screen_width * 3 / 12) - ((screen_width * 6 / 12) - 78)) / 2)
# print(277 + 402 * 3 + 78*2)
# print(1639 - 1920)

# print(954 - 1294)
# print(717 - 921)

# li = []

# if type(li) == list:
#     print("成功")

# while True:
#     print("a")
#     break

TARGET_VID = 0x057e
TARGET_PID = 0x0306

vid = 0x057e
pid= 0x0306


REPORT_MODE_ACCEL = 0x31
HID_OUTPUT_REPORT_ID = 0x12

devices = hid.enumerate(vid, pid)
if not devices:
    print(f"エラー: 指定されたVID/PID (0x{vid:04x}/0x{pid:04x}) のWiiリモコンが見つかりません。")
    print(" -> OSのBluetooth設定でリモコンが接続済みか確認してください。")
    print(f"{hid.device}")

# 1. デバイスのオープン
path = devices[0]['path']
device = hid.device()
device.open_path(path)

print("接続成功！")
print(f" 製品名: {device.get_product_string()}")
print(f" メーカー名: {device.get_manufacturer_string()}")

a = 0

    
# reportのなかにあるデータが加速度に関するものかどうかを確かめてる
while True:
    report = device.read(22) 

    if not report[0] == REPORT_MODE_ACCEL or len(report) >= 6:

        raw_x = report[3] << 2 #通常の値が高いのに下位2ビット()気にしたところで変わらんので省略　※詳しくはwii.pyのcalculate_accelerometer関数を参照
        raw_y = report[4] << 2
        raw_z = report[5] << 2

        # print(raw_x,raw_y,raw_z)
        
        print(raw_y)
        if raw_y >= 600:
            a += 1
            print(f"とんでるらしい{a}")


