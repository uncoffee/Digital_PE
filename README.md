自分で書いたプログラムはmain_program.pyとsub_program.pyです。
test.pyやwii.pyはライブラリの検証などにしようしました。

1. pip install -r a.txtを入力してください。(ライブラリのインストール)
2. main_program.pyをpython3.13で起動してください。
3. 接続されているカメラを発見したら、arucoマーカを使用する設定に自動で切り替わります。(必要がない場合はcap = cv2.VideoCapture(0)の部分をいじってください。詳細はコメントアウトしています。)
4. wiiが接続されていればwiiを使う設定に自動で切り替わります。(wiiが接続されていないとjumpモーションと運動量の表示が出ません。)
5. 注意：使用している画像には使用させていただいているイラストが含まれています、決して無断使用や転載や改変などを行わないでください。
取説スライドのurl:[こちらをクリック](https://docs.google.com/presentation/d/1pyidMTEHStZwnk2w1CiVG76neflUliYh6idSZf6ifLw/edit?usp=sharing)