# Made by Kim.Seung.Hwan / ksana1215@interminds.ai
# -*- coding: utf-8 -*-
from tkinter import *
import tkinter.font
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image, ImageEnhance, ImageDraw
from playsound import playsound
import json
import datetime
import request_main
import config

# 키오스크 UI
class Uipage:
    def __init__(self, root, rd):
        self.rd = rd
        self.root = root
        self.root.title("INTERMINDS")
        self.cf_path = config.path['path']
        self.canvas = Canvas(self.root, height=1024, width=600)
        self.start_img = PhotoImage(file=self.cf_path + 'asset/START.png')
        self.auth_adult_img = PhotoImage(file=self.cf_path + 'asset/AUTH_ADULT.png')
        self.auth_first_img = PhotoImage(file=self.cf_path + 'asset/AUTH_FIRST.png')
        self.auth_fail_img = PhotoImage(file=self.cf_path + 'asset/AUTH_FAIL.png')
        self.shop_img = PhotoImage(file=self.cf_path + 'asset/SHOPPING.png')
        self.device_err_img = PhotoImage(file=self.cf_path + 'asset/DEVICE_ERR.png')
        self.fail_img = PhotoImage(file=self.cf_path + 'asset/DEVICE_FAIL.png')
        self.admin_img = PhotoImage(file=self.cf_path + 'asset/ADMIN.png')
        self.canvas.bind("<Button-1>", self.S_BTN)
        self.readRedis()
        self.rd.flushdb()
        self.root.attributes('-fullscreen', True)
        self.cnt = 0
        self.START_PAGE()
        self.b1 = "up"
        self.signLen = 0
        self.orderText = StringVar()
        self.RegText = StringVar()
        self.orderAmt = StringVar()
        self.drawingArea = None
        self.signImage = None
        self.xold = None
        self.yold = None

    # 시작화면 복귀
    def comeback(self):
        page_timer = self.rd.get('nowPage')
        if page_timer == None:
            pass
        elif page_timer == b'auth_adult':
            self.cnt += 1
            if self.cnt >= 1000:
                self.cnt = 0
                self.START_PAGE()
                return
        elif page_timer == b'fail':
            self.cnt += 1
            if self.cnt == 30:
                self.cnt = 0
                self.START_PAGE()
                return
        elif page_timer == b'auth_fail':
            self.cnt += 1
            if self.cnt == 30:
                self.cnt = 0
                self.START_PAGE()
                return
        elif page_timer == b'auth_first':
            self.cnt += 1
            if self.cnt == 30:
                self.cnt = 0
                self.START_PAGE()
                return
        elif page_timer == b'start':
            self.cnt = 0
            return
        else:
            self.cnt = 0
        self.root.after(1000, self.comeback)

    # 터치 버튼 이벤트
    def S_BTN(self, event):
        flg = self.rd.get('nowPage')
        if flg == None:
            pass
        elif flg == b'start':
            if 75 < event.x < 530 and 795 < event.y < 905:
                request_main.check_status()
        elif flg == b'auth_adult':
            if 75 < event.x < 530 and 795 < event.y < 905:
                self.START_PAGE()
        elif flg == b'auth_first':
            if 75 < event.x < 530 and 795 < event.y < 905:
                self.START_PAGE()
        elif flg == b'auth_fail':
            if 75 < event.x < 530 and 795 < event.y < 905:
                self.START_PAGE()

    # 시작 화면
    def START_PAGE(self):
        self.clearAllWidgets()
        self.rd.set('nowPage', 'start')
        self.canvas.create_image(0, 0, anchor=NW, image=self.start_img)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.comeback()

    # 성인 인증 요청
    def AUTH_ADULT(self):
        self.rd.set('nowPage', 'auth_adult')
        self.canvas.create_image(0, 0, anchor=NW, image=self.auth_adult_img)
        self.comeback()

    # 카카오 지갑 첫 시도
    def AUTH_FIRST(self):
        self.rd.set('nowPage', 'auth_first')
        self.canvas.create_image(0, 0, anchor=NW, image=self.auth_first_img)
        self.comeback()

    # 성인 인증 실패
    def AUTH_FAIL(self):
        self.rd.set('nowPage', 'auth_fail')
        self.canvas.create_image(0, 0, anchor=NW, image=self.auth_fail_img)
        self.comeback()

    # 문열리고 쇼핑시작
    def SHOPPING_PAGE(self):
        self.rd.set('nowPage', 'shopping')
        self.canvas.create_image(0, 0, anchor=NW, image=self.shop_img)

    # 상태조회 오류
    def FAIL_PAGE(self):
        self.rd.set('nowPage', 'fail')
        self.canvas.create_image(0, 0, anchor=NW, image=self.fail_img)
        self.comeback()

    # 키오스크 장치 오류
    def DEVICE_ERR_PAGE(self):
        self.clearAllWidgets()
        self.rd.set('nowPage', 'device_err')
        self.canvas.create_image(0, 0, anchor=NW, image=self.device_err_img)

    # 관리자 권한 점유
    def ADMIN_PAGE(self):
        self.rd.set('nowPage', 'admin')
        self.canvas.create_image(0, 0, anchor=NW, image=self.admin_img)

    # 페이지 루프
    def readRedis(self):
        try:
            msg = self.rd.get("msg")
            if msg is None:
                pass
            elif msg == b'START':
                self.START_PAGE()
                self.rd.delete('msg')

            elif msg == b'000':
                self.AUTH_ADULT()
                self.playWav('auth_kakao')
                self.rd.delete('msg')

            elif msg == b'auth_first':
                self.AUTH_FIRST()
                self.playWav('auth_first')
                self.rd.delete('msg')

            elif msg == b'001':
                self.FAIL_PAGE()
                self.playWav('device_fail')
                self.rd.delete("msg")

            elif msg == b'device_err':
                self.DEVICE_ERR_PAGE()
                self.rd.delete("msg")

            elif msg == b'auth_fail':
                self.AUTH_FAIL()
                self.playWav('auth_fail')
                self.rd.delete("msg")

            elif msg == b'shopping':
                self.SHOPPING_PAGE()
                self.playWav('shopping')
                self.rd.delete("msg")

            elif msg == b'admin':
                self.ADMIN_PAGE()
                self.playWav('admin')
                self.rd.delete("msg")

            elif msg == b'admin_close':
                self.START_PAGE()
                self.playWav('admin_close')
                self.rd.delete('msg')

            elif msg == b'door_close':
                self.START_PAGE()
                self.playWav('door_close')
                self.rd.delete('msg')

        except Exception as ex:
            pass
        self.root.after(1000, self.readRedis)

    # 음성 안내
    def playWav(self, audio_file):
        playsound(self.cf_path + 'voice/' + audio_file + ".mp3", False)

    # 위젯 초기화
    def clearAllWidgets(self):
        if self.rd.get('box') == b'o':
            self.orderAmtLabel.place_forget()
            self.orderFrame.place_forget()
            self.orderBar.pack_forget()
            self.orderBox.pack_forget()
            self.rd.delete('ol')
            self.rd.set('box', 'c')
        elif self.rd.get('box') == b'r':
            self.RegFrame.place_forget()
            self.RegBar.pack_forget()
            self.RegBox.pack_forget()
            self.rd.set('box', 'c')
        elif self.rd.get('sign') == b'o':
            self.chb_1.place_forget()
            self.chb_2.place_forget()
            if self.rd.get('check_1') == b'a':
                self.chb_1.place_forget()
                self.chb_2.place_forget()
                self.nchb_1.place_forget()
            if self.rd.get('check_2') == b'b':
                self.chb_1.place_forget()
                self.chb_2.place_forget()
                self.nchb_2.place_forget()
            if self.rd.get('check_1') == b'a' and self.rd.get('check_2') == b'a':
                self.chb_1.place_forget()
                self.chb_2.place_forget()
                self.nchb_1.place_forget()
                self.nchb_2.place_forget()
            else:
                self.chb_1.place_forget()
                self.chb_2.place_forget()
            self.rd.delete('check_1')
            self.rd.delete('check_2')
            self.drawingArea.place_forget()
            self.rd.set('sign', 'c')
