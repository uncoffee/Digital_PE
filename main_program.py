#"C:/Program Files/Python311/python.exe" pythonのインストール先
#pip install 打ち込むの忘れずにね！


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

pygame.init()

w = 1920
h = 1080
screen = pygame.display.set_mode((w, h),pygame.FULLSCREEN  | pygame.SCALED | pygame.HWSURFACE)

#変更可

#一秒間に画面更新をする回数
fps = 100 

split_varue = 20 #円が出てくるマス目の細かさ

use_aruco = False #True:設定したarucoマーカを追尾　False:マウスカードルを追尾

use_wii = False #True:wiiを使った重力加速度を使った機能を開放　False:追加機能なしで続行

comment_size = 200 #コメントのサイズを指定する

play_time = 60

#変更不可
game_point = 0

scan_count = 0


#surfaceの設定
difficulty_level = "easy"

pygame.display.set_caption("デジタル体育")

front_surface = pygame.Surface((w,h), pygame.SRCALPHA)

middle_surface = pygame.Surface((w,h), pygame.SRCALPHA)

back_surface = pygame.Surface((w,h),pygame.SRCALPHA)


circle_time = 1 #0にするとZeroDivisionErrorが出る

check_count = 0
    
def change_x(A, B, now):
    x1, y1 = A
    x2, y2 = B
    now_X, now_y = now

    return ((x1 - x2) / (y1 - y2)) * (now_y-y1) + x1

def change_y(A, B, now):
    x1, y1 = A
    x2, y2 = B
    now_x, now_y = now
    return ((y1 - y2) / (x1 - x2)) * (now_x - x1) + y1

def player_chenge_point(player):
    if use_aruco:
        for i in edge_marker_list:
            if i.name == "left_top":
                left_top = i.now_point
            if i.name == "right_top":
                right_top = i.now_point
            if i.name == "right_buttom":
                right_bottom = i.now_point
            if i.name == "left_buttom":
                left_bottom = i.now_point
        # print(f"四隅の座標 :{left_top,right_top,right_bottom,left_bottom}")

    else:
        return pygame.mouse.get_pos()
    


clock = pygame.time.Clock()

class aruco_entity:
    def __init__(self,marker_id,set_point):
        self.count = 1000 #カメラに映ってからの時間を計測に使う値。時間間隔はfps変数に依存
        self.marker_id = marker_id #arucoマーカーのid
        self.set_point = set_point
        self.now_point = (0,0) #プレイヤーの位置を特定するのに必要な値

    def count_plus1(self):#カメラに映ってからの時間を計測
        global fps
        global circle_time
        self.count += 1
    
    def set_now_point(self, now_point):#arucoマーカーの移動に対応して座標の再設定を行う.
        self.now_point = now_point
        self.count = 0
    
class edge_marker(aruco_entity):
    def __init__(self , info):
        self.info = info
        self.clear = 0 #drawした時の透明度(アルファ値)
        self.draw_point = (0,0)
        self.choice = False

        super().__init__(info["marker_id"],info["set_point"])

    def draw(self, mode):
        if mode == "set":
            if not self.count < 5:
                pygame.draw.circle(back_surface, (255,255,255),(self.set_point), 30)
            else:
                pygame.draw.circle(back_surface, (255,0,0),(self.set_point), 30)

class player_marker(aruco_entity): #画像データと座標データ分ける？
    def __init__(self,marker_id,img_name,,set_point):
        img_size = 180
        self.draw_point = (0,0)
        self.img = image_changer(img_name,img_size)
        draw_point = set_img_point(draw_point,img_size)
        self.hit_box = 0,0,0,0
        self.choice = False #画面に表示されるかどうか
        self.clear = 0 #drawした時の透明度(アルファ値)

        super().__init__(marker_id,set_point)

    def draw(self, mode):
        img_point = set_img_point(self.draw_point,self.img_size)

        self.img.set_alpha(self.clear)

        if mode == "set":
            if self.count < 5:
                back_surface.blit(self.img,self.set_point)

        if mode == "menu":
            if self.marker_id == 6:#id6は赤足
                pygame.draw.circle(front_surface, (255,255,255),player_chenge_point(self.now_point), 30)

        if mode == "play":
            if self.choice == True:
                self.clear += 20
                
                if self.clear > 255:
                    self.clear = 255
                    x , y = self.draw_point
                    self.hit_box = x-45, x+45,y-45, y+45#ここの値を後で変える。
                if self.clear == 255:                 
                    push_checker(player_chenge_point(self.now_point),self)

            else:
                self.clear -= 40
                if self.clear < 0:
                    self.clear = 0

            front_surface.blit(self.img,img_point)


    def action(self):
        random.choice(comment_list).make(self.draw_point)
        print(self.draw_point)
        count_result.touch()
        self.choice = False
        random_choice(play_entitys)
        #音を出す。

    def back_action(self):
        #文字で動きを誘導かな。(文字は写真じゃないほうがよさそう)
        print("")


class wii_entity:
    def __init__(self,img_name,img_size,setvalue):
        self.img_size = img_size
        self.img = image_changer(img_name,img_size)
        #このsetvalueにはwii認識のIDとデータ要求の値をいれる。
        self.setvalue = setvalue
            
        self.draw_point = 0,0
        self.clear = 0
        self.jump_count = 0
        self.push_count = 0
        self.hit_box = 0,0,w,h #全画面
        self.choice = True

        try:
            devices = hid.enumerate(0x057e,0x0306) #このなぞのintはデバイス(wii)識別IDです。
            if devices:
                path = devices[0]['path']
                device = hid.device()
                device.open_path(path)

            else:
                print("wiiが見つからないよ")
                #ダメだったらエラー吐かせて落とすなり専用画面に誘導なりしたい。
        
        except:
            print("デバイスがみつからねえ")

        self.device = device
 
    def draw(self,mode):
        self.draw_point = set_img_point(self.draw_point,self.img_size)

        if mode == "set":
            if self.jump_count >= 0:
                front_surface.blit(self.img,self.draw_point)

        if mode == "play":
            if self.choice:
                self.clear += 20

            else:
                self.clear -= 40

            if self.clear > 255:
                self.clear = 255
                
                report = self.device.read(22) 
                    
                    # reportのなかにあるデータが加速度に関するものかどうかを確かめてる
                if not report[0] == REPORT_MODE_ACCEL or len(report) >= 6:

                    raw_y = report[4] << 2 #通常の値が高いのに下位2ビット()気にしたところで変わらんので省略　※詳しくはwii.pyのcalculate_accelerometer関数を参照
                    
                    if raw_y >= 600:
                        self.device.set_nonblocking(False)
                        self.choice = False
                        random_choice(play_entitys)

            elif self.clear < 0:
                self.clear = 0

            else:
                if self.choice:
                    self.device.set_nonblocking(True)

        
def img_range_changer(size):
    #25この値は 666px * 375pxの画像をpygameに落とした後、描画サイズ1に対して、200分の1px画素数の値（これは半径である。）※円の画像基準
    size * 25

    #flootを使いたくなかったため倍々にした為ここで、除算をしている
    return size // 100


class coment_text:
    def __init__(self,info):
        self.img = image_changer(info["img_name"],info["size"])
        self.draw_point = (0,0)
        self.clear_range = {"max":255 ,"min":0}
        self.clear = 0

    def make(self,draw_point):
        self.draw_point = draw_point
        self.clear = self.clear_range["max"]

    def draw(self):
        self.img.set_alpha(self.clear)
        front_surface.blit(self.img,self.draw_point)

        self.clear -= 1
        if self.clear < self.clear_range["min"]:
            self.clear = self.clear_range["min"]

def count_checker():
    for i in set_entity_list:
        if i.count > 5:
            return False
    return True

        
class level_entitys:
    def __init__(self , info):
        img_size = 600
        self.img = image_changer(info["img_name"],img_size)
        self.choice = False
        self.clear = 255 #エンティティーの初期透明度の指定
        self.info = info
        
        if info["acction"] == True:
            self.clear = 0 #エンティティーの初期透明度の指定　min:0 max:255
            self.clear_range = {"max" : 255 , "min" : 0}

            if info["level"] == "easy": #初期設定として難易度をeasyにする。
                self.clear = 255 #エンティティーの初期透明度の指定　min:0 max:255
                self.choice = True
            
    def draw(self , mode):
        if mode == "menu":
            self.img.set_alpha(self.clear)
            if self.info["acction"] == True:
                middle_surface.blit(self.img, self.info["draw_point"])

            else:
                back_surface.blit(self.img, self.info["draw_point"])

    def action(self):
        self.now_clear += 10 #この値でどれくらい長押し？すればアクションが起きるかを設定できる。
        if self.now_clear > self.clear_range["max"]:
            self.now_clear = self.clear_range["max"]

            for i in level_entity_list:
                i.now_chews = False
            self.now_chews = True

            global difficulty_level
            difficulty_level = self.level_seter

    def back_action(self):
        if not self.choice == True:
            # 別のモードが選択された時に消えるスピード
            self.clear -= 60
            if self.clear < self.clear_range["min"]:
                self.clear = self.clear_range["min"]

class back_entitys:
    def __init__(self , info):
            img_size = 1800
            self.info = info
            self.img = image_changer(info["img_name"],img_size)

    def draw(self , mode):
        if mode == "menu":
            back_surface.blit(self.img, self.info["draw_point"])

class button_entity:
    def __init__(self , info):
        if info["acction"] == True:
            self.clear_range = {"max":255 ,"min":0} #一番透明な状態
            self.clear = 0 #実際の透明度の値

        else:
            self.clear = 255 #実際の透明度の値
        
        self.info = info
        img_size = 1000
        self.img = image_changer(info["img_name"],img_size)

    def draw(self , mode):
        if self.info["draw_mode"] == "menu":
            self.img.set_alpha(self.clear)
            back_surface.blit(self.img, self.info["draw_point"])

    def action(self):
        global difficulty_level
        if difficulty_level != None:
            self.clear += 5
            self.img
            if self.clear > self.clear_range["max"]:
                self.clear = 0 #またメニューに戻ってきても押せるようにリセットする。
                global mode
                global circle_time
                mode = self.info["change_mode"]

                if difficulty_level == "easy":
                    circle_time = 5

                if difficulty_level == "normal":
                    circle_time = 4

                if difficulty_level == "hard":
                    circle_time = 3

                count_timer.reset(play_time) #play_time はモードplayの持続時間
        
    def back_action(self):
        self.clear -= 20
        if self.now_clear < self.clear_range["min"]:
            self.now_clear = self.clear_range["min"]

def text_draw(text,font,draw_point,get_color = None):
    if not get_color == None:
        color = get_color
    
    else:
        color = 255,255,255

    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (draw_point)
    
    screen.blit(text_surface, text_rect)


class counter:
    def __init__(self):
        self.count_time = -1#マイナスの状態であれば表示されない。

    def count(self):
        if self.count_time <= 0:
            return True

        else:
            self.count_time -= 1
            return False
        
    def draw(self):
        if self.count_time > 0:
            text_draw(self.count_time,pygame.font.Font(None, 100),(w / 20 * 18,h / 20 * 1))

    def reset(self,time):
        self.count_time = time

        
class play_result:
    def __init__(self):
        self.combo = 0
        self.get_touch = 0
        self.miss_touch = 0
        self.score = 0

    def touch(self):
        self.get_touch += 100
        self.combo += 1

    def jump(self):
        self.score += 300
        self.combo += 1

    def draw(self):
        co = self.combo / 10
        score = self.score * co

        result_text = random.choice(result_texts)

        text_draw(f"{result_text}",pygame.font.Font(None,500),(w/2,h/4))
        text_draw(f"がんばりぽいんと:{score}",pygame.font.Font(None,200),(w/20*15,h/3*2))
        # text_draw(f"good:{self.get_touch}",pygame.font.Font(None,200),(w/20*3,h/5*3))
        # text_draw(f"miss:{self.miss_touch}",pygame.font.Font(None,200),(w/20*3,h/5*4))


def push_checker(cursor,entity):
    #aから始まるものはアンダー（底辺）に当たる座標。tから始まるものはトップ（上底）に当たる座標。
    a_x , t_x , a_y , t_y = entity.hit_box
    c_x , c_y = cursor

    if a_x <= c_x <= t_x and a_y <= c_y <= t_y:
        entity.action()

    else:
        entity.back_action()

def p(text,time):
    if time == "n":
        print(text)

    elif time % 50 == 0:
        print(text)

def set_img_point(draw_point,img_size):
    d_x , d_y = draw_point
    magnification = img_size / 180
    return (int(-90 * magnification + d_x),int(-50 * magnification + d_y))



def scan_manager(scan_count,mode):
    for j in set_entity_list:
        j.count_plus1()

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = numpy.rot90(frame)
        if mode == "set":
            opencv_cap_surface = pygame.surfarray.make_surface(frame)
            screen.blit(opencv_cap_surface,(w / 2 - 340,h * 2 / 3 - 204))

        if scan_count % 5 == 0:#この5は、5フレームのことを指す。
                
            markers, ids, rejected = aruco_detector.detectMarkers(frame)
            if ids is not None:
                for i in range(len(markers)):
                    ID = ids[i]
                    C1 = markers[i][0][0]
                    C2 = markers[i][0][1]
                    C3 = markers[i][0][2]
                    C4 = markers[i][0][3]
                    ave = int((C1[0] + C2[0] + C3[0] + C4[0]) / 4) , int((C1[1] + C2 [1] + C3[1] + C4[1]) / 4)

                    for j in set_entity_list:
                        if j.marker_id == int(ID):
                                j.set_now_point(ave)




def menu_manager(cursor):
    for i in menu_entity_list:
        draw_x , draw_y = i.draw_point
        i.img.set_alpha(i.now_clear)

        if i.move:
            push_checker(cursor,i)
            middle_surface.blit(i.img, (draw_x , draw_y))

        else:
            back_surface.blit(i.img, (draw_x , draw_y))




#処理で使うためのクラスをまとめたリスト
all_entity = []
set_entity_list = [] #arucoマーカの座標を管理するクラスのリスト
menu_entity_list = []#mode = "menu"の時に使うクラスのリスト
play_entitys = [] #mode = "play"の時に使うクラスのリスト

#------------------------------------------------------------------------

comment_list = [
    coment_text({"img_name":"good.png" ,"size":400}),
]

#------------------------------------------------------------------------

edge_marker_list = [
    edge_marker({"marker_id":1 ,"ing_name":"left_top.png" ,"set_point":[int(w * 0.1),int(h * 0.1)]}),
    edge_marker({"marker_id":2 ,"ing_name":"right_top.png" ,"set_point":[int(w * 0.9),int(h * 0.1)]}),
    edge_marker({"marker_id":3 ,"ing_name":"right_buttom.png" ,"set_point":[int(w * 0.9),int(h * 0.9)]}),
    edge_marker({"marker_id":4 ,"ing_name":"left_buttom.png" ,"set_point":[int(w * 0.1),int(h * 0.9)]})
]
set_entity_list.append(edge_marker_list)

#------------------------------------------------------------------------

player_marker_list = [
    player_marker({"marker_id":5 ,"ing_name":"blue_feet.png" ,"set_point":[(w * 5 // 9) - 90,(h * 1 // 9) - 50]}),
    player_marker({"marker_id":6 ,"ing_name":"red_feet.png" ,"set_point":[(w * 5 // 9) - 90,(h * 2 // 9) - 50]}),
    player_marker({"marker_id":7 ,"ing_name":"blue_hand.png" ,"set_point":[(w * 4 // 9) - 90,(h * 1 // 9) - 50]}),
    player_marker({"marker_id":8 ,"ing_name":"red_hand.png" ,"set_point":[(w * 4 // 9) - 90,(h * 2 // 9) - 50]})
]
set_entity_list.append(player_marker_list)
play_entitys.append(player_marker_list)

#------------------------------------------------------------------------

level_entity_list = [
    level_entitys({"acction":True ,"level":"easy" ,"img_name":"moveeasy.png" ,"draw_point":((w * 3 / 12) -300,(h / 3) - 167) ,"hit_box":(277,679,242,485)}),
    level_entitys({"acction":True ,"level":"normal" ,"img_name":"movenormal.png" ,"draw_point":((w * 6 / 12) -300,(h / 3) - 167) ,"hit_box":(757,1159,242,485)}),
    level_entitys({"acction":True ,"level":"hard" ,"img_name":"movehard.png" ,"draw_point":((w * 9 / 12) -300,(h / 3) - 167) ,"hit_box":(1237,1639,242,485)}),
    level_entitys({"acction":False ,"img_name":"easy.png" ,"draw_point":((w * 3 / 12) -300,(h / 3) - 167)}),
    level_entitys({"acction":False ,"img_name":"normal.png" ,"draw_point":((w * 6 / 12) -300,(h / 3) - 167)}),
    level_entitys({"acction":False ,"img_name":"hard.png" ,"draw_point":((w * 9 / 12) -300,(h / 3) - 167)})
]
all_entity.append(level_entity_list)
menu_entity_list.append(level_entity_list)

#-----------------------------------------------------------------------

start_button_list = [
    button_entity({"acction":False ,"img_name":"start_button.png" ,"draw_point":((w / 2) -500,(h * 4 / 5) -278)}),
    button_entity({"acction":True ,"change_mode":"play" ,"draw_mode":"menu" ,"img_name":"start_button_frame.png" ,"draw_point":((w / 2) -500,(h * 4 / 5) -278) ,"hit_box":(524,1398,734,1006)})
]
all_entity.append(start_button_list)
menu_entity_list.append(start_button_list)

#------------------------------------------------------------------------

back_entity_list = [
    back_entitys({"img_name":"level_frame.png" ,"draw_point":((w / 2) - 900,(h / 2) - 500)})
]
all_entity.append(back_entity_list)
menu_entity_list.append(back_entity_list)

#------------------------------------------------------------------------

result_texts = [
    "よくがんばりました！","はなまる！","がんばれたね！","おめでとう！","めいっぱいがんばったね！","すごい！",
]
all_entity.append(result_texts)

#------------------------------------------------------------------------





if use_wii == True:
    # wiiリモコンの認識番号(ID)を設定する
    TARGET_VID = 0x057e
    TARGET_PID = 0x0306

    # Wiiリモコンから欲しいデータを要求するための値
    REPORT_MODE_ACCEL = 0x31
    HID_OUTPUT_REPORT_ID = 0x12

    jump_entity_list = [#ingsizeは後で要調整　イメージはgoogle スライド参照
        wii_entity("jump.png",1000,[(TARGET_VID,TARGET_PID),[REPORT_MODE_ACCEL,HID_OUTPUT_REPORT_ID]])
    ]

    play_entitys.append(jump_entity_list)


count_timer = counter()


count_result = play_result()


aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
aruco_params = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

cap = cv2.VideoCapture(1)
ret, frame = cap.read()
if ret != True: #while文からif文に変えた。
    use_aruco = False
    mode = "menu" #スキャンするカメラがないためメニューから。
    print("カメラが接続されていません。")
    print("現在の設定ではuse_arucoはFalseです。")
    print("カメラを使用せずに開始します。")

else:
    use_aruco = True
    print("カメラの接続が確認されました。")

scan_count = 0
count = 0


running = True
while running:
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    #fpsの値を設定
    clock.tick(fps)

    #描写のリセット
    front_surface.fill((0,0,0,0))
    middle_surface.fill((0,0,0,0))
    back_surface.fill((0,0,0,0))
    screen.fill((50,50,50))

    scan_count += 1
    scan_manager(scan_count, mode)#setmodeの時だけ妥協でカメラの画像を出力する。

    #タイマーを使いまわすためにここに配置。
    count_timer.draw()


    if mode == "set":
        for e in set_entitys:
            if e.choice == True:
                e.draw(mode="end")

        if count_checker():
            mode = "menu"

    elif mode == "menu":
        for e in menu_entitys:
            if e.choice == True:
                e.draw(mode="end")
        player = (0, 0)
        for i in player_marker_list:
            if i.marker_id == 6:#marker_idの6は"赤足.png"
                player = i
                player.draw(mode)
        
        for i in menu_entity_list:
            i.draw()

            if i.move:
                push_checker(player_chenge_point(player.now_point),i)

        if mode == "play":#mode が playになって初めの一回のみ宣言する
            make_circle()

    elif mode == "play":
        #円にふれたら新しく生成するので時間生成はなくなった
        for e in play_entitys:
            if e.choice == True:
                e.draw(mode="end")

        if scan_count % fps == 0:
            if count_timer.count():
                mode = "end"
                count_timer.reset(10)

        for i in comment_list:
            i.draw()

        if mode == "end":#mode が endになって初めの一回のみ宣言する
            fps = 1#ラグ回避のためにfpsを一時的に下げる

    elif mode == "end":
        for e in end_entitys:
            if e.choice == True:
                e.draw(mode="end")

        count_result.draw()
        if scan_count % fps == 0:
            if count_timer.count():
                mode = "menu" 
        
        if mode == "menu":#mode が menuになって初めの一回のみ宣言する
            fps = 100#デフォルトのfps 100

    screen.blit(back_surface,(0,0))

    screen.blit(middle_surface,(0,0))

    screen.blit(front_surface,(0,0))

    pygame.display.update() 

pygame.quit()
print("ウィンドウを閉じました。")

sys.exit()#ごり押し処理　修正