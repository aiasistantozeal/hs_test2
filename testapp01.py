### 事前準備 ###
#
# イベントフォルダに移動して…
#
# python -m venv .hs    ← 新しい仮想環境「.hs」を生成する
#
# .hs\Scripts\activate.bat    ← 新しい仮想環境「.hs」を起動する
# (.hs) > python -m pip install --upgrade pip     ←pip更新
# (.hs) > python -m pip install -r requirements.txt   ← ライブラリの一括インストール
# ※一括インストールは時間がかかりますので(2分～？）休み時間の前などに実行するとよいでしょう
#
# requirements.txt の内容
#   streamlit             ← 毎度、おなじみ
#   typing_extensions     ← これがないとエラーが出ることがあるので一応
#   numpy                 ← 毎度、おなじみ
#   pandas                ← 毎度、おなじみ
#   folium                ←地図表示用
#   streamlit-folium      ←地図表示用
#   opencv-python         ←画像処理ライブラリ
#   pyzbar                ←QRコード読み取り
#
# (.hs) > streamlit run testapp01.py    ← Webアプリ（testapp01.py）を起動

### アプリの原案
# 安積疏水の水路に沿ったウォーキングアプリ
# 目的：安積疏水の歴史に触れながら家族団らんや運動の機会を設ける。
# 機能
# ・現在地点をリアルタイムに取得しアプリ上に反映させる。
# ・距離に応じたランク制度を設けて競争心を出しやすくする。
# ・宝探しイベントを開催し、キーワードを集めて景品と交換できるようにする
# 				↓↑OR
# ・目標距離を達成するとポイントがもらえ貯めて景品と交換できる。
# ・エリアが分かれているので地域別もしくは、全エリア制覇型にする。
# 景品
# ・安積疏水は農業などにも利用されてきた歴史があるので
# 県産の野菜や米といった地域にゆかりがあるものや
# 宿泊券、クーポンなどを利用できるようにする。
# クーポン
# ・公共の交通機関で現地に向かう場合に割引されるものがあると利用者が増えそう。
# 管理
# ・県もしくは市区町村に委託する
# （宝探しの問題は地域の学生から募っても面白そう）
#

### やること ###
#
# 1.距離の計算、どのくらい歩いた
# 2.現在地を取得
# 3.チェックポイント　位置情報マッピング
# 参考URL（https://qiita.com/akatin/items/fbc0fe6b23ce514acd0f）
# 参考URL2(https://chayarokurokuro.hatenablog.com/entry/2020/09/02/212350)
# マップアイコンの種類公式（https://glyphsearch.com/?library=glyphicons）
# 4.掲示板機能　風景写真の投稿など

#############
#####^^^^####
###^######^##
###^######^##
#####^^^^####
# 距離と時間、ポイント健康ポイント

# デプロイしたアプリURL（https://aiasistantozeal-hs-app01-testapp01-2qgpdt.streamlitapp.com/）
#
# -----------------------------------------------------

# ライブラリのインポート
from sys import _xoptions
import streamlit as st
from PIL import Image, ImageOps
import numpy as np

# 地図表示ライブラリ
import folium #pip install folium
from streamlit_folium import folium_static # pip install streamlit-folium
# import streamlit as st
import pandas as pd

# QRコード読み取り関係ライブラリ
import cv2 as cv
#import numpy as np
from pyzbar.pyzbar import decode
import webbrowser
#import streamlit as st

#------------------------------------------------------
# 中間ポイント用の緯度経度データを作成する
checkPoint = pd.DataFrame(
    data=[[37.4,140.3],
          [37.5,140.3],
          [37.5,140.25],
          [37.5,140.2]],
    index=["中間ポイント１","中間ポイント２","中間ポイント３","中間ポイント４"],
    columns=["x","y"]
)

# 現在地用の緯度経度データ
yourLocation_x = 37.25
yourLocation_y = 140.3

yourLocation = pd.DataFrame(
    data=[[yourLocation_x,yourLocation_y]],
    index=["現在地"],
    columns=["x","y"]
)

# QRコードのポイント関係変数初期化
poi = 4

#-------------------------------------------------------
#-------------------------------------------------------
# データを地図に渡す関数を作成する
def AreaMarker(df,m,rad):
    for index, r in df.iterrows(): 

        # ピンをおく
        folium.Marker(
            location=[r.x, r.y],
            popup=index,
            icon = folium.Icon(color="blue",icon="star")
        ).add_to(m)

        # 円を重ねる
        folium.Circle(
            radius=rad*1000,
            location=[r.x, r.y],
            popup=index,
            color="yellow",
            fill=True,
            fill_opacity=0.07
        ).add_to(m)

# 現在地を地図に渡す関数を作成する
def YourLocationMarker(df,m,rad):
    for index, r in df.iterrows(): 

        # ピンをおく
        folium.Marker(
            location=[r.x, r.y],
            popup=index,
            icon=folium.Icon(color='red',icon="map-marker")
        ).add_to(m)

        # 円を重ねる
        folium.Circle(
            radius=rad*10,
            location=[r.x, r.y],
            popup=index,
            color="red",
            fill=True,
            fill_opacity=0.07
        ).add_to(m)

# QRコード読み取り
def kamera():
    #Webカメラの読み込み
    cap = cv.VideoCapture(0)
    #出力ウィンドウの設定
    cap.set(3,640)
    cap.set(3,480)
    brea_k = 0
    while True:
        if brea_k == True:
            break
        ret,frame = cap.read()
        for barcode in decode(frame):
            print(barcode.data)
            myData = barcode.data.decode('utf-8')
            if myData is not None:

                brea_k = True
                break
            pts =np.array([barcode.polygon],np.int32)
            cv.polylines(frame,[pts],True,(255,0,0),5)
            pts2 =barcode.rect
            cv.putText(frame,myData,(pts2[0],pts2[1]),cv.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
        cv.imshow('test',frame)
        if cv.waitKey(1) == 13:
            break
    return myData

#-------------------------------------------------------
#-------------------------------------------------------
# メインモジュール
def main():

    # タイトル
    st.title("安積疏水の水路に沿ったウォーキングアプリ")

    # QRコード読み取り
    st.subheader("★QRコード読み取ってポイントを貰おう！★")
    if st.button("QRコードを読み取る", key=0):
        Pit = kamera()
        if Pit is not None:
            st.header("獲得ポイント＜{}ポイント＞".format(Pit))
            poi = poi + int(Pit)
            st.header("現在の合計ポイントは{}ポイント".format(poi))


    # 地図表示
    #rad = st.slider('拠点を中心とした円の半径（km）',
                #value=40,min_value=5, max_value=50) # スライダーをつける
    rad = 40
    #st.write("各拠点からの距離{:,}km".format(rad)) # 半径の距離を表示
    m = folium.Map(location=[yourLocation["x"],yourLocation["y"]], zoom_start=9) # 地図の初期設定
    AreaMarker(checkPoint ,m,rad) # データを地図渡す
    YourLocationMarker(yourLocation, m,rad) #現在地を地図に渡す
    folium_static(m) # 地図情報を表示

#-------------------------------------------------------
#-------------------------------------------------------

# mainの起動
if __name__ == "__main__":
    main()


#=============================================================================#
# 氏名：佐藤光
# 学校：国際情報工科自動車大学校
# 学科：AIシステム科
# 学年：２年
#
#=============================================================================#
