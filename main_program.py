#"C:/Program Files/Python311/python.exe" pythonのインストール先
#pip install 打ち込むの忘れずにね！


#pip要る
import pygame 
import cv2 #pip install opencv-python モジュ:pip install opencv-contrib-python
import hid #pip install hidapi
import math

#pipいらない
from sub_program import image_changer , random_choice , draw_text , print_check
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
fps = 10

split_varue = 20 #円が出てくるマス目の細かさ

comment_size = 200 #コメントのサイズを指定する

play_time = 10

#変更不可
game_point = 0

scan_count = 0

mode = "set"

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
            if i.info["ing_name"] == "left_top.png":
                left_top = i.now_point
            if i.info["ing_name"] == "right_top.png":
                right_top = i.now_point
            if i.info["ing_name"] == "right_buttom.png":
                right_bottom = i.now_point
            if i.info["ing_name"] == "left_buttom.png":
                left_bottom = i.now_point
        # print(f"left_top: {left_top} right_top: {right_top} right_bottom: {right_bottom} left_bottom: {left_bottom}")

    else:
        return pygame.mouse.get_pos()
    
    left_x = change_x(left_top,left_bottom,player)
    right_x = change_x(right_top,right_bottom,player)

    mouse_x = int(w * 0.8 * (player[0] - left_x) / (right_x - left_x) + w * 0.1)
    #print(f"横 :{left_x,player[0],right_x, mouse_x}")

    top_y = change_y(left_top,right_top,player)
    bottom_y = change_y(left_bottom,right_bottom,player)

    mouse_y = int(h * 0.8 * (player[1] -  top_y) / (bottom_y - top_y) + h * 0.1) #多分なんかやらかしてる。ああああああああああああああああああああああああああああああああああああああああ

    #print(f"縦 :{top_y,player[1],bottom_y, mouse_y}")

    return mouse_x , mouse_y
    


clock = pygame.time.Clock()

class aruco_entity:
    def __init__(self,marker_id,set_point):
        self.count = 1000 #カメラに映ってからの時間を計測に使う値。時間間隔はfps変数に依存
        self.marker_id = marker_id #arucoマーカーのid
        self.set_point = set_point
        self.now_point = (0,0) #プレイヤーの位置を特定するのに必要な値

    def count_plus1(self):#カメラに映ってからの時間を計測
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
            if self.count < 5:
                pygame.draw.circle(back_surface, (255,0,0),(self.set_point), 30)
                
            else:
                pygame.draw.circle(back_surface, (255,255,255),(self.set_point), 30)
                

class player_marker(aruco_entity): #画像データと座標データ分ける？
    def __init__(self,info):
        self.info = info
        self.img_size = 180
        self.draw_point = (0,0)
        self.img = image_changer(info["img_name"],self.img_size)
        self.choice = False #画面に表示されるかどうか
        self.clear = 0 #drawした時の透明度(アルファ値)
        self.guide_marker = False #Trueならメニューの時に追従してくれる。

        if info["img_name"] == "red_feet.png":
            self.guide_marker = True

        super().__init__(info["marker_id"],info["set_point"])

    def draw(self, mode):
        img_point = set_img_point(self.draw_point,self.img_size)

        self.img.set_alpha(self.clear)

        if mode == "set":
            if self.count < 5:
                front_surface.blit(self.img,self.set_point)

        if mode == "menu":
            if self.guide_marker == True:
                pygame.draw.circle(front_surface, (255,255,255),player_chenge_point(self.now_point), 30)

        if mode == "play":
            if self.choice == True:
                self.clear += 20
                print(self.info["img_name"])
                
                if self.clear > 255:
                    self.clear = 255
                    x , y = self.draw_point
                    self.info["hit_box"] = x-45, x+45,y-45, y+45#ここの値を後で変える。 ここは画像を描画する前に無理やり切片を使って、中心にそろえてそこからの座標でHIT判定の計算をしている。できるなら、描画座標からみてどのくらい続いているかで判定をしたい。時間がない。
                if self.clear == 255:                 
                    push_checker(player_chenge_point(self.now_point),self)

            else:
                self.clear -= 30
                if self.clear < 0:
                    self.clear = 0

            front_surface.blit(self.img,img_point)

    def action(self):
        random.choice(comment_list).make(self.draw_point)
        count_result.touch()
        self.choice = False
        random_draw_point.choice(play_entitys)
        #音を出す。

    def back_action(self):
        #文字で動きを誘導かな。(文字は写真じゃないほうがよさそう)
        print("")
        
        


class jump_entity:#今のところwiiは一台のみ使用するため、classの設計も__init__を複数回たたかれることを想定していない。
    def __init__(self,info):
        #画像の大きさ
        size = 2000
        #任天堂とwiiの固有ID
        wii_vid = 0x057e
        wii_pid = 0x0306

        self.info = info
        self.img = image_changer(info["img_name"],size)
        self.choice_time = 0
        self.clear = 0
        self.choice = False
        self.use_wii = False

        try:
            devices = hid.enumerate(wii_vid,wii_pid) #このなぞのintはデバイス(wii)識別IDです。
            if devices:
                path = devices[0]['path']
                device = hid.device()
                device.open_path(path)
                self.device = device
                self.use_wii = True

            else:
                print("wiiが見つからないよ")
        
        except:
            print("デバイスがみつからねえ")

    def draw(self,mode):
        #重力加速度の値を入手するための値と、出力形式。
        report_key = 0x31

        if mode == "play":
            self.device.set_nonblocking(True)
            self.img.set_alpha(self.clear)
            front_surface.blit(self.img,self.info["draw_point"])

            report = self.device.read(22)

        if not report:
            return 
            
        # reportのなかにあるデータが加速度に関するものかどうかを確かめてる
        if not report[0] == report_key or len(report) >= 6:
            #通常の値が高いのに下位2ビット()気にしたところで変わらんので省略　※詳しくはwii.pyのcalculate_accelerometer関数を参照
            raw_x = report[3] << 2
            raw_y = report[4] << 2
            raw_z = report[5] << 2

            ave = int(raw_x + raw_y + raw_z) // 3
            print(ave)
            print(f"raw_x{raw_x} raw_y{raw_y} raw_z{raw_z}")
            point = abs(raw_x - ave) + abs(raw_y - ave) + abs(raw_z - ave)

            count_result.exercise_move(point)
            

            if self.choice == True:
                self.clear += 10
                
            else:
                self.clear -= 10

            if self.clear > 255:
                self.clear = 255

                if raw_y >= 600:#ここでジャンプ後の処理をする。
                    self.choice = False
                    random_draw_point.choice(play_entitys)

            elif self.clear < 0:
                self.clear = 0

            if mode == "end":
                self.device.set_nonblocking(False)
                    
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

    def draw(self,mode):
        if mode == "play":
            self.img.set_alpha(self.clear)
            front_surface.blit(self.img,self.draw_point)

            self.clear -= 10
            if self.clear < self.clear_range["min"]:
                self.clear = self.clear_range["min"]

def count_checker():
    for i in set_entitys:
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
            self.hit_box = info["hit_box"]

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
        self.clear += 10 #この値でどれくらい長押し？すればアクションが起きるかを設定できる。
        if self.clear > self.clear_range["max"]:
            self.clear = self.clear_range["max"]

            for i in level_entity_list:
                i.choice = False
            self.choice = True

            global difficulty_level
            difficulty_level = self.info["level"]

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
            self.hit_box = info["hit_box"]

        else:
            self.clear = 255 #実際の透明度の値
        
        self.info = info
        img_size = 1000
        self.img = image_changer(info["img_name"],img_size)

    def draw(self , mode):
        if self.info["draw_mode"] == mode:
            self.img.set_alpha(self.clear)
            if self.info["acction"] == True:
                middle_surface.blit(self.img, self.info["draw_point"])

            else:
                back_surface.blit(self.img, self.info["draw_point"])

    def action(self):
        global difficulty_level
        if difficulty_level != None:
            self.clear += 30
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
        self.clear -= 60
        if self.clear < self.clear_range["min"]:
            self.clear = self.clear_range["min"]

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
            time_drawer.draw(f"{self.count_time}")

    def reset(self,time):
        self.count_time = time

        
class play_result:
    def __init__(self):
        self.combo = 0
        self.get_touch = 0
        self.miss_touch = 0
        self.score = 0
        self.exercise = 0

    def touch(self):
        self.get_touch += 100
        self.combo += 1

    def jump(self):
        self.score += 100
        self.combo += 1

    def exercise_move(self,value):
        self.exercise += value

    def reset(self):
        self.score = 0
        self.exercise = 0

    def draw(self):
        co = self.combo / 10
        self.score = self.score * co

        result_score_drawer.draw(f"touch:{self.score}")\nexercise:{self.exercise}

class result_comment:
    def __init__(self,info):
        self.choice = False
        self.text_surface , self.text_rect = result_comment_drawer.get_data(info["comment"])

    def draw(self):
        if self.choice == True:
            front_surface.blit(self.text_surface , self.text_rect)

def push_checker(cursor,entity):
    #aから始まるものはアンダー（底辺）に当たる座標。tから始まるものはトップ（上底）に当たる座標。
    a_x , t_x , a_y , t_y = entity.info["hit_box"]
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
    for j in set_entitys:
        j.count_plus1()

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
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

                    for j in set_entitys:
                        if j.info["marker_id"] == int(ID):
                                j.count = 0
                                j.set_now_point(ave)

#sub_programのクラスをたたく。
random_choicer = random_choice()
random_draw_point = random_choice({"padding":100,"near":100,"width":w,"height":h})
time_drawer = draw_text({"draw_point":(w / 20 * 18,h / 20 * 1),"pallet":screen,"font":pygame.font.Font(None, 100),"color":(255,255,255),"Anti_Aliasing":True})
result_comment_drawer =  draw_text({"draw_point":(w/2,h/4),"pallet":screen,"font":pygame.font.Font(None,500),"color":(255,255,255),"Anti_Aliasing":True})
result_touch_drawer = draw_text({"draw_point":(w//2 ,h/3*2),"pallet":screen,"font":pygame.font.Font(None,200),"color":(255,255,255),"Anti_Aliasing":True})
result_exercise_drawer = draw_text({"draw_point":(0,h/5*4),"pallet":screen,"font":pygame.font.Font(None,200),"color":(255,255,255),"Anti_Aliasing":True})

pri = print_check()

#時間計測+表示のクラス
count_timer = counter()

#運動スコアの表示
count_result = play_result()

#arucoマーカの指定
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
aruco_params = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

#処理で使うためのクラスをまとめたリスト
set_entitys = [] #mode = "set"の時に使うクラスのリスト
menu_entitys = []#mode = "menu"の時に使うクラスのリスト
play_entitys = [] #mode = "play"の時に使うクラスのリスト

#------------------------------------------------------------------------

comment_list = [
    coment_text({"img_name":"good.png" ,"size":400}),
]
play_entitys += comment_list

#------------------------------------------------------------------------

edge_marker_list = [
    edge_marker({"marker_id":1 ,"ing_name":"left_top.png" ,"set_point":[int(w * 0.1),int(h * 0.1)]}),
    edge_marker({"marker_id":2 ,"ing_name":"right_top.png" ,"set_point":[int(w * 0.9),int(h * 0.1)]}),
    edge_marker({"marker_id":3 ,"ing_name":"right_buttom.png" ,"set_point":[int(w * 0.9),int(h * 0.9)]}),
    edge_marker({"marker_id":4 ,"ing_name":"left_buttom.png" ,"set_point":[int(w * 0.1),int(h * 0.9)]})
]
set_entitys += edge_marker_list

#------------------------------------------------------------------------

player_marker_list = [
    player_marker({"marker_id":5 ,"acction":True ,"img_name":"blue_feet.png" ,"set_point":[(w * 5 // 9) - 90,(h * 1 // 9) - 50]}),
    player_marker({"marker_id":6 ,"acction":True ,"img_name":"red_feet.png" ,"set_point":[(w * 5 // 9) - 90,(h * 2 // 9) - 50]}),
    player_marker({"marker_id":7 ,"acction":True ,"img_name":"blue_hand.png" ,"set_point":[(w * 4 // 9) - 90,(h * 1 // 9) - 50]}),
    player_marker({"marker_id":8 ,"acction":True ,"img_name":"red_hand.png" ,"set_point":[(w * 4 // 9) - 90,(h * 2 // 9) - 50]})
]
set_entitys += player_marker_list
play_entitys += player_marker_list

#------------------------------------------------------------------------

back_entity_list = [
    back_entitys({"acction":False ,"img_name":"level_frame.png" ,"draw_point":((w / 2) - 900,(h / 2) - 500)})
]
menu_entitys += back_entity_list

#------------------------------------------------------------------------

level_entity_list = [
    level_entitys({"acction":True ,"level":"easy" ,"img_name":"moveeasy.png" ,"draw_point":((w * 3 / 12) -300,(h / 3) - 167) ,"hit_box":(277,679,242,485)}),
    level_entitys({"acction":True ,"level":"normal" ,"img_name":"movenormal.png" ,"draw_point":((w * 6 / 12) -300,(h / 3) - 167) ,"hit_box":(757,1159,242,485)}),
    level_entitys({"acction":True ,"level":"hard" ,"img_name":"movehard.png" ,"draw_point":((w * 9 / 12) -300,(h / 3) - 167) ,"hit_box":(1237,1639,242,485)}),
    level_entitys({"acction":False ,"img_name":"easy.png" ,"draw_point":((w * 3 / 12) -300,(h / 3) - 167)}),
    level_entitys({"acction":False ,"img_name":"normal.png" ,"draw_point":((w * 6 / 12) -300,(h / 3) - 167)}),
    level_entitys({"acction":False ,"img_name":"hard.png" ,"draw_point":((w * 9 / 12) -300,(h / 3) - 167)})
]
menu_entitys += level_entity_list

#-----------------------------------------------------------------------

button_list = [
    button_entity({"acction":False ,"draw_mode":"menu","img_name":"start_button.png" ,"draw_point":((w / 2) -500,(h * 4 / 5) -278)}),
    button_entity({"acction":True ,"change_mode":"play" ,"draw_mode":"menu" ,"img_name":"start_button_frame.png" ,"draw_point":((w / 2) -500,(h * 4 / 5) -278) ,"hit_box":(524,1398,734,1006)})
]
menu_entitys += button_list

#------------------------------------------------------------------------

result_comments = [
    result_comment({"comment":"nt"}),
    result_comment({"comment":"nf"}),
    result_comment({"comment":"sokosoko"}),
    result_comment({"comment":"ome"}),
    result_comment({"comment":"ganbattane"}),
    result_comment({"comment":"grate"})
]

#------------------------------------------------------------------------

wii = jump_entity({"acction":True ,"img_name":"jump.png" ,"draw_point":(0,0)})
if wii.use_wii == True:
    play_entitys.append(wii)
    print("wiiを使います。")

#------------------------------------------------------------------------

cap = cv2.VideoCapture(1)#ノーパソの標準カメラは1くそやすいカメラは2(環境により変動します)
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
    if use_aruco == True:
        scan_manager(scan_count, mode)#setmodeの時だけ妥協でカメラの画像を出力する。

    #タイマーを使いまわすためにここに配置。
    count_timer.draw()

    if mode == "set":
        for e in set_entitys:
            e.draw(mode)

        if count_checker():
            mode = "menu"

    elif mode == "menu":
        for e in menu_entitys:
            e.draw(mode)

        player = (0, 0)
        for i in player_marker_list:
            if i.marker_id == 6:#marker_idの6は"赤足.png"
                player = i
                player.draw(mode)
        
        for i in menu_entitys:
            i.draw(mode)

            if i.info["acction"] == True:
                push_checker(player_chenge_point(player.now_point),i)

        if mode == "play":#mode が playになって初めの一回のみ宣言する
            random_draw_point.choice(player_marker_list)

    elif mode == "play":
        #円にふれたら新しく生成するので時間生成はなくなった
        for i in play_entitys:
            i.draw(mode)

        if scan_count % fps == 0:
            if count_timer.count():
                mode = "end"
                count_timer.reset(10)

        if mode == "end":#mode が endになって初めの一回のみ宣言する
            random_choicer.choice(result_comments)#お疲れ様の一言。
            fps = 1#ラグ回避のためにfpsを一時的に下げる

            for i in play_entitys:
                i.choice = False

    elif mode == "end":

        count_result.draw()
        if scan_count % fps == 0:
            if count_timer.count():
                mode = "menu" 
        
        if mode == "menu":#mode が menuになって初めの一回のみ宣言する
            fps = 10#デフォルトのfps 30
            count_result.reset()


    screen.blit(back_surface,(0,0))

    screen.blit(middle_surface,(0,0))

    screen.blit(front_surface,(0,0))

    pygame.display.update() 

pygame.quit()
print("ウィンドウを閉じました。")

sys.exit()#ごり押し処理　修正