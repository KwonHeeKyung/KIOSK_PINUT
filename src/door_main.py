# Made by Kim.Seung.Hwan / ksana1215@interminds.ai
# -*- coding: utf-8 -*-
import threading

import serial
import redis
import logging
import datetime
import config
import urllib3
from playsound import playsound
import request_main
cf_path = config.path['path']
cf_door_port = config.refrigerators['door']
rd = redis.StrictRedis(host='localhost', port=6379, db=0)
Arduino = serial.Serial(port=cf_door_port, baudrate=9600, timeout=0.1)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(filename=cf_path+'kiosk_status.log',level=logging.DEBUG)
logger = logging.getLogger('UNO_LOG')
cnt = 0

def alarm():
    status = rd.get('door')
    global cnt
    if status == b'customer' or status == b'admin_open':
        cnt += 1
        if cnt > 600:
            logger.info(log_time)
            if status == b'customer':
                playsound(cf_path + 'voice/' + "long.mp3", False)
                rd.set('err_type', 'long')
                request_main.device_err()
                cnt = 0
            elif status == b'admin_open':
                playsound(cf_path + 'voice/' + "longlong.mp3", False)
                cnt = 0

        threading.Timer(1, alarm).start()
    else:
        cnt = 0
        return

while True:
    log_time = datetime.datetime.now()
    log_time = log_time.strftime("%Y-%m-%d-%H:%M:%S")
    door = rd.get('door')
    try:
        uno = Arduino.readline().decode('utf-8').rstrip()
        #문열림
        if door == b'open':
            Arduino.write(str('1').encode('utf-8'))
            rd.set('door', 'customer')
            logger.info(f'[{log_time} | DOOR_OPEN --> CLIENT]')
            request_main.door_open()
            alarm()

        #관리자 문열림
        if door == b'admin':
            Arduino.write(str('1').encode('utf-8'))
            rd.set('door', 'admin_open')
            request_main.admin_open()
            alarm()

        #문닫힘
        if uno == '0':
            #관리자 권한
            if door == b'admin_open':
                request_main.admin_close()
            #고객
            elif door == b'customer':
                logger.info(f'[{log_time} | DOOR_CLOSE --> CLIENT]')
                rd.delete('door')
                # rd.set('msg', 'door_close')
                request_main.door_close()
        #문여닫힘 에러
        if uno == '2':
            rd.set('err_type','except')
            request_main.device_err()
            logger.info(f'[{log_time} | DOOR LOCK ERR]')
    except Exception as err:
        rd.set('err_type', 'except')
        rd.set('msg', 'device_err')
        rd.delete('door')
        request_main.device_err()
        logger.info(f'[{log_time} | ARDUINO FAIL]' + '\n' + str(err))
        break